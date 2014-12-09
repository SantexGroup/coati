from datetime import datetime
from flask import session, redirect, url_for, blueprints, request

from app.schemas import Token
from tools import get_provider, get_user_data


__author__ = 'gastonrobledo'

blueprint = blueprints.Blueprint('auth', __name__, url_prefix='/auth')


def init_app(app):
    app.register_blueprint(blueprint)


def get_user():
    return session.get('user')


# # Routes
@blueprint.route('/authenticate')
def authenticate():
    oauth_provider = request.args.get('provider', 'google')
    session['provider'] = oauth_provider
    session['callback_url'] = request.args.get('callback')
    user = session.get('user')
    if user is None:
        return redirect(url_for('auth.login'))
    else:
        access_token = Token.get_token_by_user(user['_id']['$oid'])
        expire_in = (access_token.expire - datetime.now()).seconds
        return redirect('%s?token=%s&expire=%s' % (session.get('callback_url'),
                                                   access_token.token,
                                                   expire_in))


@blueprint.route('/login')
def login():
    callback = url_for('auth.authorized', _external=True)
    prov = get_provider(session.get('provider'),
                        authorized_handler=authorized)
    return prov.authorize(callback=callback)


@blueprint.route('/authorized')
def authorized():
    provider = get_provider(session.get('provider'),
                            authorized_handler=authorized)
    if 'oauth_verifier' in request.args:
        data = provider.handle_oauth1_response()
    elif 'code' in request.args:
        data = provider.handle_oauth2_response()
    else:
        data = provider.handle_unknown_response()
    provider.free_request_token()
    access_token = data['access_token']
    user = get_user_data(access_token)
    Token.save_token_for_user(user,
                              access_token=access_token,
                              provider=provider.name,
                              expire_in=data['expires_in'])
    session['user'] = user
    return redirect('%s?token=%s&expire=%s' % (session.get('callback_url'),
                                               access_token,
                                               data['expires_in']))


@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect('/login?logout=true')


