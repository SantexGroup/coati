from flask import session, redirect, url_for, blueprints, request

from tools import get_provider, get_user_data, generate_token, authorize_data
from app.utils import serialize_data

blueprint = blueprints.Blueprint('auth', __name__, url_prefix='/auth')


def init_app(app):
    app.register_blueprint(blueprint)

# # Routes
@blueprint.route('/authenticate')
def authenticate():
    return redirect(url_for('auth.login',
                            provider=request.args.get('provider'),
                            client_callback=request.args.get('callback'),
                            next=request.args.get('next')))


@blueprint.route('/login')
def login():
    callback = url_for('auth.authorized', _external=True)
    prov = get_provider(request.args.get('provider'))
    extra_params = {'state': serialize_data({
        'provider': request.args.get('provider'),
        'callback': request.args.get('client_callback'),
        'next': request.args.get('next')
    })}
    prov.request_token_params.update(extra_params)
    return prov.authorize(callback=callback)


@blueprint.route('/authorized')
def authorized():
    return redirect(authorize_data())


@blueprint.route('/logout')
def logout():
    session.clear()
    return redirect('/login?logout=true')


