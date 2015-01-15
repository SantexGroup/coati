__author__ = 'gastonrobledo'

ENVIRONMENT = "local"


# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
if ENVIRONMENT == 'local':
    CURRENT_DOMAIN = 'http://localhost:5000'
    SOCKET_IO = 'http://localhost:9000'
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
        }
    }
else:
    CURRENT_DOMAIN = 'http://agile.santextest.com'
    SOCKET_IO = 'http://agile.santextest.com:8001'
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
            'consumer_key': '1082545664750-80pj871en76r9q2147rok59ahkh4njpl.apps.googleusercontent.com',
            'consumer_secret': 'nfsVJdlUgUKMcJXuiOa397FK'
        },
        'facebook': {
            'base_url': 'https://graph.facebook.com/',
            'request_token_url': None,
            'access_token_url': '/oauth/access_token',
            'authorize_url': 'https://www.facebook.com/dialog/oauth',
            'request_token_params': {'scope': 'email'},
            'consumer_key': '765019266901164',
            'consumer_secret': '77e164a607da0c0b55189af5c63a31fb'
        },
        'github': {
            'base_url': 'https://github.com/login',
            'authorize_url': 'https://github.com/login/oauth/authorize',
            'request_token_url': None,
            'request_token_params': {'scope': 'user:email,public_repo'},
            'access_token_url': 'https://github.com/login/oauth/access_token',
            'consumer_key': 'c76ff1faa4fb0eeb895a',
            'consumer_secret': '969726f58eb49b876def2f281c2d0251b43c34a0'
        }
    }

PROVIDERS_INFO = {
    'google': 'https://www.googleapis.com/oauth2/v1/userinfo',
    'facebook': 'https://graph.facebook.com/me',
    'github': 'https://api.github.com/user'
}

SECRET_KEY = 'AIzaSyD2QbbC8fr-Eob-qWitXDqBP1tZCBr5Gcw'
#seconds to expire 30000 aprox 8hs
TOKEN_EXPIRATION_TIME = 30000
DEBUG = True

if ENVIRONMENT == 'local':
    FRONTEND = 'build'
else:
    FRONTEND = 'bin'

MONGODB_DB = 'coati'
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_USERNAME = ''
PASSWORD = ''

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = True
MAIL_USERNAME = 'gaston.robledo@santexgroup.com'
MAIL_PASSWORD = '!G@5t0NR0bl3d0'
MAIL_DEFAULT_SENDER = 'gaston.robledo@santexgroup.com'

REDIS_URL = 'redis://:c04t1@localhost:6379/0'