from datetime import datetime
from flask import session, redirect, url_for, blueprints, request

from app.schemas import Token
from tools import get_provider, get_user_data, generate_token


__author__ = 'gastonrobledo'

blueprint = blueprints.Blueprint('auth', __name__, url_prefix='/auth')


def init_app(app):
    app.register_blueprint(blueprint)

# # Routes
@blueprint.route('/authenticate')
def authenticate():
    oauth_provider = request.args.get('provider', 'google')
    session['provider'] = oauth_provider
    session['callback_url'] = request.args.get('callback')
    return redirect(url_for('auth.login'))


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
    if user:
        token = generate_token(str(user.pk))
        Token.save_token_for_user(user,
                                  app_token=token,
                                  social_token=access_token,
                                  provider=provider.name,
                                  expire_in=10000)

        return redirect('%s?token=%s&expire=%s' % (session.get('callback_url'),
                                                   token,
                                                   10000))
    else:
        return redirect(session.get('callback_url'))


@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect('/login?logout=true')


