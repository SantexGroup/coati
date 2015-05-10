from mongoengine import errors

from flask import request, current_app
from flask_restful import Resource

from coati.core.models.user import User
from coati.web.api import errors as api_errors


class AccessToken(Resource):
    """
    AccessToken resource.
    """

    def post(self):
        """
        Endpoint for token requests.
        Creates a new access token based on provided credentials.
        :return: JSON with the token, refresh token and expiration time
        """
        data = request.get_json(silent=True)

        if data:
            email = data.get('email')
            password = data.get('password')

            try:
                user = User.objects.get(email=email, active=True)
            except errors.DoesNotExist:
                raise api_errors.UnauthorizedRequest(
                    api_errors.INVALID_CREDENTIALS_MSG
                )

            if not user.verify_password(password):
                raise api_errors.UnauthorizedRequest(
                    api_errors.INVALID_CREDENTIALS_MSG
                )

            tokens_dict = current_app.token_handler.generate_tokens_dict(
                user.pk
            )

            return tokens_dict, 200

        raise api_errors.InvalidAPIUsage(
            api_errors.INVALID_JSON_BODY_MSG
        )


class RefreshToken(Resource):
    """
    RefreshToken resource.
    """

    def post(self):
        """
        Endpoint for token refreshing.
        Takes a refresh token from a JSON body and issues a new
        access token.
        :return: A new token with a new expiration time.
        """
        data = request.get_json(silent=True)

        if data:
            refresh = data.get('refresh_token')
            expire = current_app.token_handler.expires_in
            new_token = current_app.token_handler.refresh_token(refresh)

            if not new_token:
                raise api_errors.UnauthorizedRequest(
                    api_errors.INVALID_REFRESH_TOKEN_MSG
                )

            return dict(token=new_token, expires_in=expire), 200

        raise api_errors.InvalidAPIUsage(
            api_errors.INVALID_JSON_BODY_MSG
        )
