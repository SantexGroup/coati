from flask import jsonify
from flask.ext.restful import Resource, request
from werkzeug.exceptions import BadRequest

from app.api.schemas import User, Project, Ticket

class ProjectList(Resource):

    def __init__(self):
        super(ProjectList, self).__init__()


    def get(self):
        return Project.objects.all().to_json(), 200

    def post(self):
        """
        Create Project
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
        prj.save()
        return prj.to_json(), 201


class ProjectInstance(Resource):

    def get(self, slug):
        return Project.objects.get(slug=slug).to_json()

    def put(self, slug):
        project = Project.objects.get(slug=slug)
        data = request.json
        project.active = data.get('active', project.active)
        project.description = data.get('description', project.description)
        project.name = data.get('name', project.name)
        owner = User.objects.get(id=data.get('owner'))
        project.owner = owner or project.owner
        project.private = data.get('private', project.private)
        project.save()
        return project.to_json(), 200

    def delete(self, slug):
        project = Project.objects.get(slug=slug)
        project.delete()
        return {}, 204


class UsersList(Resource):

    def __init__(self):
        super(UsersList, self).__init__()


    def get(self):
        return User.objects.all().to_json()


class UserInstance(Resource):

    def __init__(self):
        super(UserInstance, self).__init__()

    def get(self, pk):
        return User.objects.get(id=pk).to_json()

    def put(self, pk):
        pass

    def delete(self, pk):
        pass


class Tickets(Resource):

    def __init__(self):
        super(Tickets, self).__init__()

    def get(self, project_pk):
        return Ticket.objects(project=project_pk).to_json()

    def post(self, project_pk):
        """
        Create Project
        """
        try:
            data = request.json
        except BadRequest, e:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        try:
            project = Project.objects.get(id=project_pk)
        except Project.DoesNotExist, e:
            return jsonify({"error": 'project does not exist'}), 400

        tkt = Ticket(project=project.to_dbref())
        tkt.description = data.get('description')
        tkt.labels = data.get('labels')
        tkt.title = data.get('title')
        tkt.save()
        return tkt.to_json(), 201