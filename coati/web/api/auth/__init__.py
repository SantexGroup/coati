"""
Authentication resource.
"""

from flask import request, current_app, g as flask_g
from flask.ext.restful import Resource

from coati.core.models.user import User
from coati.web.api import errors
from coati.web.api.auth import oauth, utils, decorators
from coati.web.api.auth.utils import current_user  # noqa

oauth_handler = None


def get_user_from_token():
    """
    Parses an Access Token and stores either the User or an error on Flask's
    globals object.
    It's important to use this function just once, in order to validate the
    token only at the beginning of the request.
    """
    try:
        token = utils.parse_auth_header()
    except errors.BasicAPIException as ex:
        flask_g.auth_error = ex
    else:
        user_obj = utils.parse_auth_token(token)

        if user_obj:
            # Store the user for the current request
            utils.set_current_user(user_obj)


class Authorized(Resource):
    """
    Social authorization resource.
    """

    def post(self):
        """
        Social authorization endpoint.
        """
        request_data = request.get_json(silent=True)

        # Check required data
        if not request_data:
            raise errors.InvalidAPIUsage(errors.INVALID_JSON_BODY_MSG)

        provider_name = request_data.get('provider')
        provider = oauth_handler.get_provider(provider_name)
        if not provider:
            raise errors.InvalidAPIUsage(errors.PROVIDER_INVALID_MSG)

        access_token = request_data.get('token')
        if not access_token:
            raise errors.InvalidAPIUsage(errors.MISSING_PROVIDER_TOKEN_MSG)

        user_id = request_data.get('user_id')
        if not user_id:
            raise errors.InvalidAPIUsage(errors.MISSING_PROVIDER_USER_ID_MSG)

        # Validate the token
        error_msg = provider.validate_token(access_token, user_id)
        if error_msg:
            raise errors.UnauthorizedRequest(errors.PROVIDER_INVALID_TOKEN_MSG)

        user_data = provider.get_user_data(access_token)

        if not user_data:
            raise errors.BasicAPIException(errors.PROVIDER_INVALID_RESP_MSG)

        # On new email, register the user
        user, _ = User.get_or_create(**user_data)
        user.save()

        tokens_dict = current_app.token_handler.generate_tokens_dict(user.id)

        return dict(tokens_dict), 200


class AuthResource(Resource):
    """
    Base resource that handles authentication and permissions.
    """

    decorators = [
        decorators.require_permissions,
        decorators.require_authentication
    ]


def init_app(app):
    """
    Perform authentication initialization.
    :param app: Flask application.
    """
    # A global is used instead of a current_app attribute because the handler
    # is only required here
    global oauth_handler
    oauth_handler = oauth.get_oauth_handler(app.config)


