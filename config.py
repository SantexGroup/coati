__author__ = 'gastonrobledo'

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
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
        'consumer_key': '966349433267.apps.googleusercontent.com',
        'consumer_secret': 'a21-EeeVh6hdYUPgapG7bYBG'
    },
    'facebook': {
        'base_url': 'https://graph.facebook.com/',
        'request_token_url': None,
        'access_token_url': '/oauth/access_token',
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'request_token_params': {'scope': 'email'},
        'consumer_key': '1422138561348620',
        'consumer_secret': 'db35b6a3f8f3560727009bcce92a0769'
    },
    'github': {
        'base_url': 'https://github.com/login',
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'request_token_url': None,
        'request_token_params': {'scope': 'user:email,public_repo'},
        'access_token_url': 'https://github.com/login/oauth/access_token',
        'consumer_key': 'eb6e366244235f181f59',
        'consumer_secret': 'f47d7ec2bfc4a1d81d2d705a59430d8e1d537ff2'
    },
    'bitbucket': {
        'base_url': 'https://bitbucket.org/api/1.0/oauth',
        'authorize_url': 'https://bitbucket.org/api/1.0/oauth/request_token',
        'request_token_url': None,
        'request_token_params': {'scope': 'user'},
        'access_token_url': 'https://bitbucket.org/api/1.0/oauth/authenticate',
        'consumer_key': 'zudHGL66HCmbRABuYS',
        'consumer_secret': 'sE42FX9mqhdDrdc9Y2qxv573LNTHwZXF'
    }
}

PROVIDERS_INFO = {
    'google': 'https://www.googleapis.com/oauth2/v1/userinfo',
    'facebook': 'https://graph.facebook.com/me',
    'github': 'https://api.github.com/user'
}

SECRET_KEY = 'AIzaSyD2QbbC8fr-Eob-qWitXDqBP1tZCBr5Gcw'
DEBUG = True

FRONTEND = 'build'

MONGODB_DB = 'coati'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_USERNAME = ''
PASSWORD = ''