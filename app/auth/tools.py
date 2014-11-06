import json
from flask import session, current_app, redirect, url_for
from flask.ext.oauth import OAuth
from app.schemas import User


def get_provider(oauth_provider, authorized_handler):
    oauth = OAuth()
    conf = current_app.config['PROVIDERS'].get(oauth_provider or 'google')
    prov = oauth.remote_app(oauth_provider, register=True, **conf)
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

    return user