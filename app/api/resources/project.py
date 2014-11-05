__author__ = 'gastonrobledo'

from flask import jsonify
from flask.ext.restful import Resource, request
from werkzeug.exceptions import BadRequest

from app.schemas import User, Project


class ProjectList(Resource):

    def __init__(self):
        super(ProjectList, self).__init__()


    def get(self):
        return Project.objects.all().to_json(), 200

    def post(self):
        """
        Create Project
        """
        data = request.get_json(force=True, silent=True)
        if not data:
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
        data = request.get_json(force=True, silent=True)
        if not data:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
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