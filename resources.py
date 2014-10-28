from flask import jsonify
from flask.ext.restful import Resource, request
from werkzeug.exceptions import BadRequest
from schemas import User, Column, Project


class ProjectList(Resource):

    def __init__(self):
        super(ProjectList, self).__init__()


    def get(self):
        return Project.objects.all().to_json(), 200

    def post(self):
        """
        Create Project with 3 default columns
        """
        try:
            data = request.json
        except BadRequest, e:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        try:
            user = User.objects.get(id=data.get('owner'))
        except User.DoesNotExist, e:
            return jsonify({"error": 'owner user does not exist'}), 400

        prj = Project(name=data.get('name'),
                      owner=user.to_dbref())
        prj.active = data.get('active')
        prj.private = data.get('private')
        prj.description = data.get('description')
        for idx in ['ToDo', 'In Progress', 'Done']:
            column = Column()
            column.title = idx
            prj.columns.append(column)
        prj.save()
        return prj.to_json(), 201


class ProjectInstance(Resource):

    def get(self, slug):
        return Project.objects(slug=slug).to_json()

    def put(self, project_id):
        pass

    def delete(self, project_id):
        pass


class UsersList(Resource):

    def __init__(self):
        super(UsersList, self).__init__()


    def get(self):
        return User.objects.all().to_json()

    def post(self):
        data = request.json
        usr = User()
        usr.email = data.get('email')
        usr.first_name = data.get('first_name')
        usr.last_name = data.get('last_name')
        usr.save()
        return usr.to_json(), 201