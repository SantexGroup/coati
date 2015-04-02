"""
Authentication helpers.
"""

from datetime import datetime

import itsdangerous
from flask import current_app, request, g as flask_g
from werkzeug.local import LocalProxy

from coati.core.models import user
from coati.web.api import errors as api_errors


current_user = LocalProxy(lambda: get_current_user())


def get_current_user():
    """
    Returns the current logged in user, or None.
    """
    return flask_g.get('user', None)


def set_current_user(user):
    """
    Save user information on Flask globals for this request.
    :param user: A user instance.
    """
    flask_g.user = user


def parse_auth_header():
    """
    Parses the Authorization Header (if any) for the current request.
    :return: The access token from the header or an unauthorized exception.
    :raise api_errors.UnauthorizedRequest: When the header is missing/invalid.
    """
    auth_header = request.headers.environ.get('HTTP_AUTHORIZATION')

    if not auth_header:
        raise api_errors.UnauthorizedRequest(
            api_errors.MISSING_AUTH_HEADER_MSG
        )

    if 'Token' not in auth_header or len(auth_header.split()) != 2:
        raise api_errors.UnauthorizedRequest(
            api_errors.INVALID_AUTH_HEADER_MSG
        )

    return auth_header.split()[1]


def parse_auth_token(token):
    """
    Parses an Access Token to retrieve the user.
    :param token: An access token.
    :return: The User for which the token was generated, or None on failure.
    """
    # Validate the token and extract its data
    token_data = current_app.token_handler.get_data(token)

    if token_data:
        user_id = token_data.get('id')

        if user_id:
            user = users.User.get_by_id(user_id)

            return user


def _get_token_data(serializer, token):
    """
    Returns data contained in a valid token.
    :param serializer: The serializer instance.
    :param token: The token to deserialize.
    :return: A dictionary data if the token is valid, `None` otherwise.
    """
    try:
        data = serializer.loads(token)
        return data
    except itsdangerous.SignatureExpired:
        current_app.logger.debug('Expired token {}'.format(token))

    except itsdangerous.BadSignature:
        current_app.logger.debug('Invalid token {}'.format(token))


class TokenHandler(object):
    """
    Handles tokens generation and validation.
    All tokens are signed. Access tokens expire after `expires_in` seconds,
    but refresh tokens do not expire.
    :ivar secret: A secret key to be used for encryption.
    :ivar expires_in: Time in seconds a token is valid (default: 3600).
    :ivar timed_serializer: The serializer for access tokens.
    :ivar serializer: The serializer for refresh tokens.
    """

    DEFAULT_EXPIRES_IN = 3600

    def __init__(self, secret, expires_in=DEFAULT_EXPIRES_IN):
        self.secret = secret
        self.expires_in = int(expires_in)

        self.timed_serializer = itsdangerous.TimedJSONWebSignatureSerializer(
            self.secret,
            expires_in=self.expires_in
        )
        self.serializer = itsdangerous.JSONWebSignatureSerializer(self.secret)

    def generate_access_token(self, data):
        """
        Generates a new access token with the provided data.
        :param data: A dictionary containing data to save in the token.
        :return: A timed and signed token.
        """
        return self.timed_serializer.dumps(data)

    def get_access_token_data(self, token):
        """
        Returns data contained in a valid access token.
        :param token: The token to deserialize.
        :return: A dictionary data if the token is valid, `None` otherwise.
        """
        return _get_token_data(self.timed_serializer, token)

    def generate_refresh_token(self, data):
        """
        Generates a new refresh token with the provided data.
        :param data: A dictionary containing data to save in the token.
        :return: A signed token.
        """
        # Add a timestamp to the token to avoid token repetition
        timestamped_data = data.copy()
        timestamped_data.update(
            {'timestamp': datetime.utcnow().strftime('%s')}
        )

        return self.serializer.dumps(timestamped_data)

    def get_refresh_token_data(self, token):
        """
        Returns data contained in a valid refresh token.
        :param token: The token to deserialize.
        :return: A dictionary data if the token is valid, `None` otherwise.
        """
        return _get_token_data(self.serializer, token)

    def generate_tokens(self, obj_id):
        """
        Generates a new access token and a refresh token.
        :param obj_id: The ID of an object in the database.
        :return: A timed and signed token.
        """
        data = {'id': str(obj_id)}

        access_token = self.generate_access_token(data)
        refresh_token = self.generate_refresh_token(data)

        return access_token, refresh_token

    def generate_tokens_dict(self, obj_id):
        """
        Generates new access and refresh tokens and returns them in a dict
        along with the expiration time in seconds.
        :param obj_id: The ID of an object in the database.
        :return: A dict containing access_token, refresh_token and expires_in.
        """
        access_token, refresh_token = self.generate_tokens(obj_id)

        return dict(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.expires_in
        )

    def refresh_token(self, refresh_token):
        """
        Generate a new access token using a refresh token.
        :param refresh_token: A refresh token.
        :return: A new access token if the refresh token is valid, `None`
            otherwise.
        """
        if not refresh_token:
            return

        data = self.get_refresh_token_data(refresh_token)

        if not data or 'timestamp' not in data:
            return

        data.pop('timestamp')

        return self.generate_access_token(data)

    get_data = get_access_token_data