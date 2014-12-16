import json, time
from itsdangerous import JSONWebSignatureSerializer
from flask import session, current_app, redirect, url_for, g, request
from flask.ext.oauth import OAuth
from mongoengine import DoesNotExist
from app.schemas import User, Token


def get_provider(oauth_provider):
    oauth = OAuth()
    conf = current_app.config['PROVIDERS'].get(oauth_provider or 'google')
    prov = oauth.remote_app(oauth_provider, register=True, **conf)
    prov.authorized_handler(authorize_data)
    prov.tokengetter(get_token)
    return prov


def authorize_data():
    provider_name = session.get('provider')
    provider = get_provider(provider_name)
    if 'oauth_verifier' in request.args:
        data = provider.handle_oauth1_response()
    elif 'code' in request.args:
        data = provider.handle_oauth2_response()
    else:
        data = provider.handle_unknown_response()

    provider.free_request_token()
    access_token = data['access_token']
    session['access_token'] = access_token
    user = get_user_data(access_token, provider, provider_name)
    if user:
        token = generate_token(str(user.pk))
        Token.save_token_for_user(user,
                                  app_token=token,
                                  social_token=access_token,
                                  provider=provider.name,
                                  expire_in=10000)

        return '%s?token=%s&expire=%s' % (session.get('callback_url'),
                                                   token,
                                                   10000)
    else:
        return session.get('callback_url')


def get_token(token=None):
    return session.get('access_token'), ''


def get_user_data(access_token, provider, provider_name):
    from urllib2 import Request, urlopen, URLError
    types = {
        'github': 'token',
        'google': 'OAuth',
        'facebook': 'OAuth'
    }
    headers = {
        'Authorization': types.get(provider_name) + ' ' + access_token}
    info_url = current_app.config['PROVIDERS_INFO'].get(provider_name)
    req = Request(info_url, None, headers)
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session['access_token'] = None
            return redirect(url_for('auth.login'))
        return res.read()

    data = json.loads(res.read())
    user = extract_data(data, provider, provider_name)
    return user


def extract_data(data, provider, provider_name):
    u = None
    if provider_name == 'google' and data['verified_email']:
        if data.get('email'):
            try:
                u = User.objects.get(email=data.get('email'))
            except DoesNotExist, e:
                u = User(email=data.get('email'))
                u.first_name = data.get('given_name')
                u.last_name = data.get('family_name')
                u.save()

    if provider_name == 'facebook' and data['verified']:
        if data.get('email'):
            try:
                u = User.objects.get(email=data.get('email'))
            except DoesNotExist, e:
                u = User(email=data.get('email'))
                u.first_name = data.get('first_name')
                u.last_name = data.get('last_name')
                u.save()
    if provider_name == 'github' and data is not None:
        names = data.get('name')
        email = data.get('email')

        if not email:
            url = current_app.config['PROVIDERS_INFO'].get(provider_name)
            extra_data = provider.get(url + '/emails')
            if extra_data.status == 200:
                for em in extra_data.data:
                    if em['primary'] and em['verified']:
                        email = em['email']
                        break

        try:
            u = User.objects.get(email=email)
        except DoesNotExist, e:
            u = User(email=email)
            if names:
                u.first_name = names
                u.save()
    return u


def generate_token(user_id):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.dumps({'pk': user_id, 'time': time.time()})


def get_data_from_token(token):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.loads(token)