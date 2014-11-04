__author__ = 'gastonrobledo'
import json

from flask_oauth import OAuth
from flask import session, redirect, url_for, blueprints, request, current_app

from app.schemas import User


blueprint = blueprints.Blueprint('auth', __name__)


def init_app(app):
    app.register_blueprint(blueprint)


def get_user():
    return session.get('user')


def get_provider(oauth_provider):
    oauth = OAuth()
    conf = current_app.config['PROVIDERS'].get(oauth_provider or 'google')
    prov = oauth.remote_app(oauth_provider, register=True, **conf)
    prov.authorized_handler(authorized)
    prov.tokengetter(get_access_token)
    return prov


# # Routes
@blueprint.route('/authenticate')
def authenticate():
    oauth_provider = request.args.get('provider', 'google')
    session['provider'] = oauth_provider
    access_token = session.get('access_token')
    user = session.get('user')
    if access_token is None or user is None:
        return redirect(url_for('auth.login'))
    else:
        return redirect(url_for('index'))


def adquire_user(token):
    from urllib2 import Request, urlopen, URLError

    types = {
        'github': 'token',
        'google': 'OAuth',
        'facebook': 'OAuth'
    }
    headers = {
        'Authorization': types.get(session.get('provider')) + ' ' + token}
    info_url = current_app.config['PROVIDERS_INFO'].get(session.get('provider'))
    req = Request(info_url, None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('auth.login'))
        return res.read()

    data = json.loads(res.read())
    extract_data(data)
    return redirect(url_for('index'))


@blueprint.route('/login')
def login():
    callback = url_for('auth.authorized', _external=True)
    prov = get_provider(session.get('provider'))
    return prov.authorize(callback=callback)


@blueprint.route('/authorized')
def authorized():
    provider = get_provider(session.get('provider'))
    if 'oauth_verifier' in request.args:
        data = provider.handle_oauth1_response()
    elif 'code' in request.args:
        data = provider.handle_oauth2_response()
    else:
        data = provider.handle_unknown_response()
    provider.free_request_token()
    access_token = data['access_token']
    session['access_token'] = access_token, ''
    return adquire_user(access_token)


def get_access_token():
    return session.get('access_token')


def extract_data(data):
    user, created = None, False
    provider = session.get('provider')
    if provider == 'google' and data['verified_email']:
        user, created = User.objects.get_or_create(email=data.get('email'),
                                                   first_name=data.get(
                                                       'given_name'),
                                                   last_name=data.get(
                                                       'family_name'))
    if provider == 'facebook' and data['verified']:
        user, created = User.objects.get_or_create(email=data.get('email'),
                                                   first_name=data.get(
                                                       'first_name'),
                                                   last_name=data.get(
                                                       'last_name'))
    if provider == 'github' and data is not None:
        prov = get_provider(provider)
        url = current_app.config['PROVIDERS_INFO'].get(session.get('provider'))
        emails = prov.get(url + '/emails').data
        if emails is not None:
            em = emails[0]
            names = data.get('name').split(' ')
            user, created = User.objects.get_or_create(email=em.get('email'),
                                                       first_name=names[0],
                                                       last_name=names[1])

    session['user'] = user.to_json()


@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

