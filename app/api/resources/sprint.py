__author__ = 'gastonrobledo'

from flask import jsonify, request
from flask.ext.restful import Resource

from app.schemas import Sprint, Project


class SprintOrder(Resource):
    def __init__(self):
        super(SprintOrder, self).__init__()

    def post(self, project_pk):
        data = request.get_json(force=True, silent=True)
        if data:
            for index, s in enumerate(data):
                sprint = Sprint.objects.get(pk=s)
                sprint.order = index
                sprint.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class SprintList(Resource):
    def __init__(self):
        super(SprintList, self).__init__()

    def get(self, project_pk):
        return Sprint.objects(project=project_pk).order_by('order').to_json()

    def post(self, project_pk):
        """
        Create Sprint
        """
        try:
            project = Project.objects.get(id=project_pk)
        except Project.DoesNotExist, e:
            return jsonify({"error": 'project does not exist'}), 400
        total = Sprint.objects(project=project_pk).count()
        sp = Sprint(project=project.to_dbref())
        sp.name = 'Sprint %d' % (total + 1)
        sp.save()
        return sp.to_json(), 201


class SprintInstance(Resource):
    def get(self, sp_id):
        sp = Sprint.objects.get(pk=sp_id)
        return sp.to_json, 200

    def delete(self, sp_id):
        sp = Sprint.objects.get(pk=sp_id)
        sp.delete()
        return sp.to_json(), 204