import os
import logging
from logging import FileHandler

from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine

from app import api, auth, utils, core
from auth import decorators


app = Flask(__name__)
app.config.from_pyfile('../config.py')
app.static_folder = 'frontend/' + app.config['FRONTEND']
app.static_url_path = '/static'


db = MongoEngine(app)
core.init_app(app)
# # Init apps
auth.init_app(app)
# # Init Api
api.init_app(app)


# # Default Routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html', config=app.config)


