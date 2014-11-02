import os
from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, blueprints, render_template, session
from flask.ext.mongoengine import MongoEngine
from app import api, auth

blueprint = blueprints.Blueprint('main', __name__,
                                 static_folder='frontend',
                                 template_folder='/')

app = Flask(__name__)
app.config.from_pyfile('../config.py')
db = MongoEngine(app)

app_path = os.path.dirname(os.path.abspath(__file__))
frontend_templates = app_path + '/frontend/' + app.config['FRONTEND']
fsLoader = FileSystemLoader(searchpath=frontend_templates)
custom_loader = ChoiceLoader([
    app.jinja_loader,
    fsLoader
])
app.jinja_loader = custom_loader

app.register_blueprint(blueprint)

# # Init apps
auth.init_app(app)
# # Init Api
api.init_app(app)


## Default Routes
@app.route('/')
def index():
    user = session.get('user')
    if not user:
        return render_template('login.html')
    else:
        return to_angular(path='', user=user)


@app.route('/<path:path>')
def to_angular(path, user=None):
    return render_template('index.html', user=user)


