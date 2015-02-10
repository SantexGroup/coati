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

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Flask app secret key
SECRET_KEY = os.getenv('SECRET_KEY')

# For example: mongodb://localhost:27017
DATABASE_URI = os.getenv('COATI_DATABASE_URI')
# For example: coati
DATABASE_NAME = os.getenv('COATI_DATABASE_NAME')

REDIS_URL = os.getenv('COATI_REDIS_URL')

MONGODB_SETTINGS = {
    'db': DATABASE_NAME,
    'host': DATABASE_URI
}
# Current App Domain
CURRENT_DOMAIN = os.getenv('CURRENT_DOMAIN')
# Socket url listener
SOCKET_IO = os.getenv('SOCKET_IO_URL')
# List of OAuth providers.
PROVIDERS = {
    'google': {
        'base_url': 'https://www.google.com/accounts/',
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'request_token_url': None,
        'request_token_params': {
            'scope': 'https://www.googleapis.com/auth/userinfo.email',
            'response_type': 'code'},
        'access_token_url': 'https://accounts.google.com/o/oauth2/token',
        'access_token_method': 'POST',
        'access_token_params': {'grant_type': 'authorization_code'},
        'consumer_key': os.getenv('GOOGLE_CONSUMER_KEY'),
        'consumer_secret': os.getenv('GOOGLE_SECRET')
    },
    'facebook': {
        'base_url': 'https://graph.facebook.com/',
        'request_token_url': None,
        'access_token_url': '/oauth/access_token',
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'request_token_params': {'scope': 'email'},
        'consumer_key': os.getenv('FACEBOOK_CONSUMER_KEY'),
        'consumer_secret': os.getenv('FACEBOOK_SECRET')
    },
    'github': {
        'base_url': 'https://github.com/login',
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'request_token_url': None,
        'request_token_params': {'scope': 'user:email,public_repo'},
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'consumer_key': os.getenv('GITHUB_CONSUMER_KEY'),
        'consumer_secret': os.getenv('GITHUB_SECRET')
    }
}

# Email settings
ADMIN_EMAILS = get_list_from_env_var(
    'ADMIN_EMAILS'
) or ['gastonrobledo@gmail.com']
EMAIL_FROM = os.getenv('EMAIL_FROM', 'gastonrobledo@gmail.com')
EMAIL_HOST = os.getenv('EMAIL_HOST', '127.0.0.1')

PROVIDERS_INFO = {
    'google': 'https://www.googleapis.com/oauth2/v1/userinfo',
    'facebook': 'https://graph.facebook.com/me',
    'github': 'https://api.github.com/user'
}
# seconds to expire 30000 aprox 8hs
TOKEN_EXPIRATION_TIME = 30000

if DEBUG:
    FRONTEND = 'build'
else:
    FRONTEND = 'bin'