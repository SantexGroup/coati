import os
import logging
from logging import FileHandler

from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, render_template
from flask.ext.mongoengine import MongoEngine

from app import api, auth, utils
from auth import decorators


app = Flask(__name__)
app.config.from_pyfile('../config.py')
app.static_folder = 'frontend/' + app.config['FRONTEND']
app.static_url_path = '/static'

file_handler = FileHandler('log.txt')
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

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
api.init_app(app)


# # Default Routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')


