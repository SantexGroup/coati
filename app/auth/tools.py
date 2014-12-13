import json, time
from itsdangerous import JSONWebSignatureSerializer
from flask import session, current_app, redirect, url_for
from flask.ext.oauth import OAuth
from mongoengine import DoesNotExist
from app.schemas import User


def get_provider(oauth_provider, authorized_handler=None):
    oauth = OAuth()
    conf = current_app.config['PROVIDERS'].get(oauth_provider or 'google')
    prov = oauth.remote_app(oauth_provider, register=True, **conf)
    if authorized_handler:
        prov.authorized_handler(authorized_handler)
    return prov


def get_user_data(access_token):
    from urllib2 import Request, urlopen, URLError

    types = {
        'github': 'token',
        'google': 'OAuth',
        'facebook': 'OAuth'
    }
    headers = {
        'Authorization': types.get(
            session.get('provider')) + ' ' + access_token}
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
    user = extract_data(data)
    return user


def extract_data(data):
    u = None
    provider = session.get('provider')
    if provider == 'google' and data['verified_email']:
        if data.get('email'):
            try:
                u = User.objects.get(email=data.get('email'))
            except DoesNotExist, e:
                u = User(email=data.get('email'))
                u.first_name = data.get('given_name')
                u.last_name = data.get('family_name')
                u.save()

    if provider == 'facebook' and data['verified']:
        if data.get('email'):
            try:
                u = User.objects.get(email=data.get('email'))
            except DoesNotExist, e:
                u = User(email=data.get('email'))
                u.first_name = data.get('first_name')
                u.last_name = data.get('last_name')
                u.save()
    if provider == 'github' and data is not None:
        names = data.get('name').split(' ')
        email = data.get('email')
        if email:
            try:
                u = User.objects.get(email=data.get('email'))
            except DoesNotExist, e:
                u = User(email=data.get('email'))
                if names:
                    u.first_name = names[0]
                    u.last_name = names[1]
                    u.save()
    return u


def generate_token(user_id):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'pk': user_id, 'time': time.time()})


def get_data_from_token(token):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.loads(token)