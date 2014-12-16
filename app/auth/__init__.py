from datetime import datetime
from flask import session, redirect, url_for, blueprints, request, g

from app.schemas import Token
from tools import get_provider, get_user_data, generate_token, authorize_data


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
    prov = get_provider(session.get('provider'))
    return prov.authorize(callback=callback)


@blueprint.route('/authorized')
def authorized():
    return redirect(authorize_data())


@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect('/login?logout=true')


