"""
OAuth helper module.
"""
import json

import flask_oauth

from flask import current_app
from werkzeug.urls import url_encode


class CustomOAuthRemoteApp(flask_oauth.OAuthRemoteApp):
    """
    Custom remote application based on `flask_oauth.OAuthRemoteApp`.
    :param validate_token_url: a function to obtain the URL for token
        validation (it should expect a token as parameter).
    :param validate_token_user: the name of the key from where to obtain user
        info on token validation.
    :param validate_token_client: the name of the key from where to obtain the
        Client ID on token validation.
    :param user_info_url: the URL to obtain user info with an access token.
    :param oauth: the associated :class:`OAuth` object.
    :param name: then name of the remote application.
    :param request_token_url: the URL for requesting new tokens.
    :param access_token_url: the URL for token exchange.
    :param authorize_url: the URL for authorization.
    :param consumer_key: the application specific consumer key.
    :param consumer_secret: the application specific consumer secret.
    :param request_token_params: an optional dictionary of parameters
                                 to forward to the request token URL
                                 or authorize URL depending on oauth
                                 version.
    :param access_token_params: an option diction of parameters to forward to
                                the access token URL.
    :param access_token_method: the HTTP method that should be used
                                for the access_token_url.  Defaults
                                to ``'GET'``.
    """

    def __init__(self,
                 validate_token_url=None,
                 validate_token_user=None,
                 validate_token_client=None,
                 user_info_url=None,
                 *args, **kwargs):

        super(CustomOAuthRemoteApp, self).__init__(*args, **kwargs)

        self.validate_token_url = validate_token_url
        self.validate_token_user = validate_token_user
        self.validate_token_client = validate_token_client
        self.redirect_uri = 'postmessage'
        self.user_info_url = user_info_url

    @staticmethod
    def get_user_info_headers(access_token):
        """
        Returns headers to obtain user info from the provider.
        :param access_token: Oauth access token.
        :return: A headers dict.
        """
        return {
            'Authorization': 'Bearer {}'.format(access_token),
        }

    def get_user_data(self, access_token):
        """
        Request and parse user information from the provider.
        :param access_token: OAuth access token.
        :return: A dictionary containing necessary user data (first_name,
            last_name and email).
        """
        raise NotImplementedError()

    def exchange_authorization_code(self, code):
        """
        Handles an oauth2 authorization response.
        :param code: The authorization code.
        :return: The data obtained from exchanging the code (at least an access
            token).
        :raise flask_oauth.OAuthException: If an unsupported method to obtain
            the access token is configured, or if an invalid response is
            received from the provider.
        """
        remote_args = dict(
            code=code,
            client_id=self.consumer_key,
            client_secret=self.consumer_secret,
            redirect_uri=self.redirect_uri
        )
        remote_args.update(self.access_token_params)

        if self.access_token_method == 'POST':
            resp, content = self._client.request(
                self.expand_url(self.access_token_url),
                method=self.access_token_method,
                body=url_encode(remote_args),
            )
        elif self.access_token_method == 'GET':
            url = flask_oauth.add_query(
                self.expand_url(self.access_token_url),
                remote_args
            )
            resp, content = self._client.request(
                url,
                method=self.access_token_method
            )
        else:
            raise flask_oauth.OAuthException(
                'Unsupported access_token_method: {}'.format(
                    self.access_token_method
                )
            )

        data = flask_oauth.parse_response(resp, content)

        if not self.status_okay(resp):
            raise flask_oauth.OAuthException(
                'Invalid response from {}'.format(self.name),
                type='invalid_response', data=data
            )

        return data

    @staticmethod
    def get_data_from_validation(data):
        """
        Helper to parse data from a token validation endpoint.
        """
        return data

    @staticmethod
    def error_handler(data=None, message=None):
        """
        Helper to log an error messages.
        :param data: Optional data for debugging.
        :param message: A custom (optional) error message.
        :return: The error message.
        """
        error_msg = message or 'Invalid token'

        current_app.logger.debug(error_msg)

        if data:
            current_app.logger.debug(data)

        return error_msg

    def request_token_validation(self, access_token):
        """
        Perform the request to validate an access token.
        :param access_token: Oauth access token.
        :return: a (response, data) tuple.
        """
        url = self.validate_token_url(access_token)

        try:
            response, content = self._client.request(url)
        except Exception as ex:
            current_app.logger.debug(ex)

            return self.validation_error

        return response, flask_oauth.parse_response(response, content)

    def validate_token(self, access_token, user_id=None):
        """
        Validate an access token obtained from the provider.
        :param access_token: OAuth access token.
        :param user_id: The user ID from the provider.
        :return: `None` if the validation succeeds, an error message otherwise.
        """
        response, data = self.request_token_validation(access_token)
        data = self.get_data_from_validation(data)

        if not self.status_okay(response):
            return self.error_handler(data=data)

        provider_user = data.get(self.validate_token_user)
        _client = data.get(self.validate_token_client)

        # Verify that the access token is used for the intended user
        is_valid_user = provider_user and provider_user == user_id

        # Verify that the access token is valid for this app
        is_valid_client = _client and _client == self.consumer_key

        if not (is_valid_user and is_valid_client):
            return self.error_handler()


class GoogleOauth(CustomOAuthRemoteApp):
    """
    Google remote application.
    """

    def get_user_data(self, access_token):
        """
        Request and parse user information from Google.
        :param access_token: OAuth access token.
        :return: A dictionary containing necessary user data (first_name,
            last_name and email).
        """
        response, content = self._client.request(
            self.user_info_url,
            headers=self.get_user_info_headers(access_token)
        )

        if not self.status_okay(response):
            return

        data = flask_oauth.parse_response(response, content)

        user_data = dict(
            first_name=data.get('given_name'),
            last_name=data.get('family_name'),
            email=data.get('email')
        )

        return user_data


class GithubOauth(CustomOAuthRemoteApp):
    """
    Github remote application.
    """

    def get_user_data(self, access_token):
        """
        Request and parse user information from Google.
        :param access_token: OAuth access token.
        :return: A dictionary containing necessary user data (first_name,
            last_name and email).
        """
        response, content = self._client.request(
            self.user_info_url,
            headers=self.get_user_info_headers(access_token)
        )

        if not self.status_okay(response):
            return

        data = flask_oauth.parse_response(response, content)

        user_data = dict(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email')
        )

        return user_data


class FacebookOauth(CustomOAuthRemoteApp):
    """
    Facebook remote application.
    """

    @staticmethod
    def get_data_from_validation(data):
        """
        Helper to parse data from a token validation endpoint.
        """
        return data.get('data')

    def get_user_data(self, access_token):
        """
        Request and parse user information from Facebook.
        :param access_token: OAuth access token.
        :return: A dictionary containing necessary user data (first_name,
            last_name and email).
        """
        remote_args = dict(
            access_token=access_token
        )
        url = flask_oauth.add_query(
            self.expand_url(self.user_info_url),
            remote_args
        )
        resp, content = self._client.request(
            url,
            method=self.access_token_method
        )

        if self.status_okay(resp):
            content = json.loads(content)
            user_data = {
                'first_name': content.get('first_name'),
                'last_name': content.get('last_name'),
                'email': content.get('email')
            }
        else:
            user_data = {}

        return user_data


# Subclassing is necessary in case the class type is used in the library
class CustomOAuth(flask_oauth.OAuth):
    """
    Custom registry for remote applications, based on `flask_oauth.OAuth`.
    """

    def get_provider(self, provider_name):
        """
        Gets the correct provider based on provider_name.
        :param provider_name: The providers name.
        :return: Remote app object representing the provider.
        """
        if not provider_name:
            return

        if not self.remote_apps:
            raise ValueError('No providers defined.')

        return self.remote_apps.get(provider_name)

    def remote_app(self, name, register=True, **kwargs):
        """
        Creates and registers a new remote application.
        :param name: The name of the app.
        :param register: Whether to register the app or not.
        :param kwargs: Keyword arguments forwarded to the
            `CustomOAuthRemoteApp` constructor.
        :return: The newly created `CustomOAuthRemoteApp`.
        """
        app = CustomOAuthRemoteApp(self, name, **kwargs)

        if register:
            self.register_app(app)

        return app

    def register_app(self, app):
        """
        Registers a new remote application.
        :param app: A `CustomOAuthRemoteApp` instance.
        """
        if app.name in self.remote_apps:
            raise AssertionError('Application already registered')

        self.remote_apps[app.name] = app


def get_oauth_handler(config):
    """
    Returns an OAuth handler with configured providers.
    :param config: Flask application config.
    :return: An oauth handler.
    """
    providers = config.get('PROVIDERS')

    oauth_handler = CustomOAuth()

    for provider_config in providers:
        new_app = None
        provider_name = provider_config.get('name')

        if provider_name.startswith('google'):
            new_app = GoogleOauth(oauth=oauth_handler, **provider_config)

        if provider_name.startswith('facebook'):
            new_app = FacebookOauth(oauth=oauth_handler, **provider_config)

        if provider_name.startswith('github'):
            new_app = GithubOauth(oauth=oauth_handler, **provider_config)

        if new_app:
            oauth_handler.register_app(new_app)
        else:
            # Register a custom app for this provider
            oauth_handler.remote_app(**provider_config)

    return oauth_handler