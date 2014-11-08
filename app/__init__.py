import os, json
from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, render_template, session
from flask.ext.mongoengine import MongoEngine
from app import api, auth, utils
from auth import decorators

app = Flask(__name__)
app.config.from_pyfile('../config.py')
app.static_folder = 'frontend/' + app.config['FRONTEND']
app.static_url_path = '/static'

db = MongoEngine(app)

app_path = os.path.dirname(os.path.abspath(__file__))
frontend_templates = app_path + '/frontend/' + app.config['FRONTEND']
fsLoader = FileSystemLoader(searchpath=frontend_templates)
custom_loader = ChoiceLoader([
    app.jinja_loader,
    fsLoader
])
app.jinja_loader = custom_loader
# # Init apps
auth.init_app(app)
# # Init Api
api.init_app(app, decorators=[decorators.require_authentication])


# # Default Routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    if session.get('user'):
        user = session.get('user')
    else:
        user = ''
    return render_template('index.html', user=user)


