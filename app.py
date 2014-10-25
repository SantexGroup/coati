from bson.json_util import dumps
from flask import Flask, make_response
from flask.ext.mongoengine import MongoEngine
from flask.ext.restful import Api
from resources import ProjectList, ProjectInstance


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
    resp = make_response(dumps(obj._collection_obj.find(obj._query)), code)
    resp.headers.extend(headers or {})

    return resp


DEFAULT_REPRESENTATIONS = {'application/json': output_json}
api = Api(app)
api.representations = DEFAULT_REPRESENTATIONS
api.add_resource(ProjectList, '/projects')
api.add_resource(ProjectInstance, '/projects/<string:project_id>')

if __name__ == '__main__':
    app.run(debug=True)
