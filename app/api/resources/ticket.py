__author__ = 'gastonrobledo'

from flask import jsonify
from flask.ext.restful import Resource, request
from werkzeug.exceptions import BadRequest
from app.schemas import Project, Ticket


class TicketList(Resource):

    def __init__(self):
        super(TicketList, self).__init__()

    def get(self, project_pk):
        return Ticket.objects(project=project_pk).to_json()

    def post(self, project_pk):
        """
        Create Project
        """
        data = request.get_json(force=True, silent=True)
        if not data:
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