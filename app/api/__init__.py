from flask.ext.restful import Api
from resources import ProjectList, ProjectInstance, UsersList
from utils import output_json


def init_app(app):
    api = Api(app, default_mediatype='application/json')
    api.add_resource(ProjectList, '/api/projects')
    api.add_resource(ProjectInstance, '/api/project/<string:slug>')
    api.add_resource(UsersList, '/api/users')
    api.representations = {'application/json': output_json}
