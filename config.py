"""
Configuration file for Flask application.
"""

import copy
import os


def get_list_from_env_var(var_name):
    """
    Returns a list from a comma separated string environment variable.
    If the env var is not defined, or empty, returns None.
    :param var_name: the ENV variable name.
    :return: a list of strings.
    """
    value = os.getenv(var_name, '')

    value = value.strip()

    # The variable was not defined or it had an empty string
    if not value:
        return

    return value.split(',')

# Statement for enabling the development environment
DEBUG = os.getenv('DEBUG', False)
JSON_INDENT = os.getenv('JSON_INDENT')

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Flask app secret key
SECRET_KEY = os.getenv('SECRET_KEY')
PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'http')
SERVER_NAME = os.getenv('SERVER_NAME')

# For example: localhost
DATABASE_HOST = os.getenv('DATABASE_HOST')
# Default: 27017
DATABASE_PORT = int(os.getenv('DATABASE_PORT', 27017))
# For example: gibike_dev
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')

MONGODB_SETTINGS = {
    'db': DATABASE_NAME,
    'host': DATABASE_HOST,
    'port': DATABASE_PORT,
    'username': DATABASE_USER,
    'password': DATABASE_PASSWORD
}

# OAuth providers configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')
FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

GOOGLE_OAUTH = dict(
    name='google',
    consumer_key=GOOGLE_CLIENT_ID,
    consumer_secret=GOOGLE_CLIENT_SECRET,
    base_url='https://www.google.com/accounts/',
    request_token_url=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    validate_token_url=lambda token: (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={token}'
        .format(token=token)
    ),
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/plus.login email',
        'response_type': 'code'
    },
    access_token_method='POST',
    access_token_params={'grant_type': 'authorization_code'},
    validate_token_user='user_id',
    validate_token_client='audience',
    # Another option for this: https://www.googleapis.com/plus/v1/people/me
    user_info_url='https://www.googleapis.com/userinfo/v2/me',
)

FACEBOOK_OAUTH = dict(
    name='facebook',
    consumer_key=FACEBOOK_CLIENT_ID,
    consumer_secret=FACEBOOK_CLIENT_SECRET,
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    validate_token_url=lambda token: (
        'https://graph.facebook.com/debug_token'
        '?input_token={token}'
        '&access_token={api_id}|{api_secret}'.format(
            token=token,
            api_id=FACEBOOK_CLIENT_ID,
            api_secret=FACEBOOK_CLIENT_SECRET
        )
    ),
    request_token_params={
        'scope': 'email'
    },
    access_token_method='GET',
    access_token_params={'grant_type': 'fb_exchange_token'},
    validate_token_user='user_id',
    validate_token_client='app_id',
    user_info_url='https://graph.facebook.com/v2.2/me',
)

# GITHUB_OAUTH = dict(
#     name='github',
#     consumer_key=GITHUB_CLIENT_ID,
#     consumer_secret=GITHUB_CLIENT_SECRET,
#     base_url='https://github.com/login',
#     request_token_url=None,
#     access_token_url='/oauth/access_token',
#     authorize_url='https://github.com/login/oauth/authorize',
#     validate_token_url=lambda token: (
#         'https://github.com/login/applications/'
#         '{client_id}/tokens/{token}'.format(
#             token=token,
#             client_id=GITHUB_CLIENT_ID
#         )
#     ),
#     request_token_params={'scope': 'user:email,public_repo'},
#     access_token_method='POST',
#     validate_token_user='user_id',
#     user_info_url='https://api.github.com/user',
# )

PROVIDERS = [
    GOOGLE_OAUTH,
    FACEBOOK_OAUTH,
    #GITHUB_OAUTH
]

# Email settings
ADMIN_EMAILS = get_list_from_env_var(
    'ADMIN_EMAILS'
) or ['gaston.robledo@santexgroup.com']
MAIL_SERVER_ERROR_FROM = os.getenv(
    'MAIL_SERVER_ERROR_FROM',
    'server-error@gibike.com'
)
MAIL_SERVER = os.getenv('MAIL_SERVER', '127.0.0.1')
MAIL_PORT = os.getenv('MAIL_PORT', 25)
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
MAIL_USE_SSL = os.getenv('MAIL_USE_SSL')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_SENDER_NAME = os.getenv('MAIL_SENDER_NAME')
# Expiration time for the password recovery token (7 days)
MAIL_RECOVERY_TOKEN_TIME = os.getenv('MAIL_RECOVERY_TOKEN_TIME', 604800)

# Token expiration time in seconds
TOKEN_EXPIRATION_TIME = os.getenv('TOKEN_EXPIRATION_TIME', 3600)

REDIS_URL = os.getenv('REDIS_URL')