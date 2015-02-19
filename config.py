"""
Configuration file for Flask application.
"""

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

# For example: mongodb://localhost:27017
DATABASE_URI = os.getenv('GIBIKE_DATABASE_URI')
# For example: coati_dev
DATABASE_NAME = os.getenv('GIBIKE_DATABASE_NAME')

MONGODB_SETTINGS = {
    'db': DATABASE_NAME,
    'host': DATABASE_URI
}
# For example: redis://:c04t1@localhost:6379/0
REDIS_URL = os.getenv('REDIS_URL')
# List of OAuth providers.
PROVIDERS = {
    'GOOGLE': {
        'base_url': 'https://www.google.com/accounts/',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'request_token_url': None,
        'request_token_params': {
            'scope': 'https://www.googleapis.com/auth/userinfo.email',
            'response_type': 'code'
        },
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'access_token_method': 'POST',
        'access_token_params': {'grant_type': 'authorization_code'},
        'consumer_key': os.getenv('GOOGLE_CLIENT_ID'),
        'consumer_secret': os.getenv('GOOGLE_CLIENT_SECRET')
    },
    'FACEBOOK': {
        'base_url': 'https://graph.facebook.com/',
        'request_token_url': None,
        'access_token_url': '/oauth/access_token',
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'request_token_params': {'scope': 'email'},
        'consumer_key': os.getenv('FACEBOOK_CLIENT_ID'),
        'consumer_secret': os.getenv('FACEBOOK_CLIENT_SECRET')
    },
    'GITHUB': {
        'base_url': 'https://github.com/login',
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'request_token_url': None,
        'request_token_params': {'scope': 'user:email,public_repo'},
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'consumer_key': os.getenv('GITHUB_CLIENT_ID'),
        'consumer_secret': os.getenv('GITHUB_CLIENT_SECRET')
    }
}

# Email settings
ADMIN_EMAILS = get_list_from_env_var(
    'ADMIN_EMAILS'
) or ['gastonrobledo@gmail.com']
EMAIL_FROM = os.getenv('EMAIL_FROM', 'server-error@coati-team.com')
EMAIL_HOST = os.getenv('EMAIL_HOST', '127.0.0.1')

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_SENDER')

# Token expiration time in seconds
TOKEN_EXPIRATION_TIME = os.getenv('TOKEN_EXPIRATION_TIME', 3600)