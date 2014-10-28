import json
from flask import Flask, session, url_for, redirect
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api
from resources import ProjectList, ProjectInstance, UsersList
from schemas import User
from flask_oauth import OAuth
from utils import output_json

# You must configure these 3 values from Google APIs console
# https://code.google.com/apis/console
GOOGLE_CLIENT_ID = '966349433267.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'a21-EeeVh6hdYUPgapG7bYBG'
REDIRECT_URI = '/authorized'  # one of the Redirect URIs from Google APIs console

SECRET_KEY = 'AIzaSyD2QbbC8fr-Eob-qWitXDqBP1tZCBr5Gcw'
DEBUG = True

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'coati',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine(app)


## Oauth google
app.secret_key = SECRET_KEY
oauth = OAuth()
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=GOOGLE_CLIENT_ID,
                          consumer_secret=GOOGLE_CLIENT_SECRET)


## Default Routes
@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
        return res.read()

    data = json.loads(res.read())
    if data['verified_email']:
        user = User.objects.get_or_create(email=data.get('email'),
                                          first_name=data.get('given_name'),
                                          last_name=data.get('family_name'))
    return ''


@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)



@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


@google.tokengetter
def get_access_token():
    return session.get('access_token')

## API
api = Api(app,
          default_mediatype='application/json')
api.add_resource(ProjectList, '/api/projects')
api.add_resource(ProjectInstance, '/api/project/<string:slug>')
api.add_resource(UsersList, '/api/users')

DEFAULT_REPRESENTATIONS = {'application/json': output_json}
api.representations = DEFAULT_REPRESENTATIONS

if __name__ == '__main__':
    app.run(debug=True)
