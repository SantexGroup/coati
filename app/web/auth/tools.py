import json
import time
from datetime import timedelta, datetime
from urllib2 import Request, urlopen, URLError

from itsdangerous import JSONWebSignatureSerializer
from flask import current_app, redirect, url_for, g, request
from flask.ext.oauth import OAuth, OAuthException
from mongoengine import DoesNotExist

from app.core.models.user import User
from app.core.models.project import ProjectMember
from app.utils import deserialize_data


def get_provider(oauth_provider):
    oauth = OAuth()
    conf = current_app.config['PROVIDERS'].get(oauth_provider or 'google')
    prov = oauth.remote_app(oauth_provider, register=True, **conf)
    prov.authorized_handler(authorize_data)
    prov.tokengetter(get_token)
    return prov


def authorize_data():
    provider_data = deserialize_data(request.args.get('state'))
    provider_name = provider_data.get('provider')
    provider = get_provider(provider_name)
    data = None
    try:
        if 'oauth_verifier' in request.args:
            data = provider.handle_oauth1_response()
        elif 'code' in request.args:
            data = provider.handle_oauth2_response()
        else:
            data = provider.handle_unknown_response()
    except OAuthException as ex:
        current_app.logger.error(ex.data)

    if data is not None:
        provider.free_request_token()
        g.access_token = data['access_token']
        user = get_user_data(g.access_token, provider, provider_name)
        if user:
            token = generate_token(str(user.pk))
            return '%s?token=%s&expire=%s&next=%s' % (
            provider_data.get('callback'),
            token,
            current_app.config['TOKEN_EXPIRATION_TIME'],
            provider_data.get('next'))
    return provider_data.get('callback')


def get_token(token=None):
    return g.access_token, ''


def get_user_data(access_token, provider, provider_name):
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
            g.access_token = None
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
            u.first_name = data.get('name')
            u.save()
    return u


def verify_token(token):
    token_data = get_data_from_token(token)
    if token_data:
        expired = token_data.get('expire')
        if datetime.fromtimestamp(expired) >= datetime.now():
            return token_data
    return None


def generate_token(user_id):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    created = time.mktime(datetime.now().timetuple())
    seconds = current_app.config['TOKEN_EXPIRATION_TIME']
    exp_date = datetime.now() + timedelta(seconds=seconds)
    expired = time.mktime(exp_date.timetuple())
    return s.dumps({'pk': user_id, 'created': created, 'expire': expired})


def get_data_from_token(token):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.loads(token)


def check_user_permissions(user_id, project_pk):
    if project_pk:
        has_perm = ProjectMember.objects(member=user_id,
                                         project=project_pk).count()
        return True if has_perm > 0 else False
    else:
        return True