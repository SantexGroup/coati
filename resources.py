import json
from bson import json_util
from flask.ext.restful import Resource, reqparse
from schemas import Project

class ProjectList(Resource):

    def get(self):
        return Project.objects()

    def post(self):
        parser = reqparse.RequestParser()
        args = parser.parse_args()
        print args


class ProjectInstance(Resource):

    def get(self, project_id):
        return Project.objects(id=project_id)

    def put(self, project_id):
        pass

    def delete(self, project_id):
        pass