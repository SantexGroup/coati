from flask import Flask, make_response
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api
from resources import ProjectList, ProjectInstance, UsersList


app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'coati',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine(app)

def output_json(obj, code, headers=None):
    """
    This is needed because we need to use a custom JSON converter
    that knows how to translate MongoDB types to JSON.
    """
    resp = make_response(obj, code)
    resp.headers.extend(headers or {})

    return resp


api = Api(app, default_mediatype='application/json')
api.add_resource(ProjectList, '/api/projects')
api.add_resource(ProjectInstance, '/api/project/<string:project_id>')
api.add_resource(UsersList, '/api/users')

DEFAULT_REPRESENTATIONS = {'application/json': output_json}
api.representations = DEFAULT_REPRESENTATIONS

if __name__ == '__main__':
    app.run(debug=True)
