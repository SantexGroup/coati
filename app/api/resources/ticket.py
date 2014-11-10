__author__ = 'gastonrobledo'

from flask import jsonify
from flask.ext.restful import Resource, request
from werkzeug.exceptions import BadRequest
from app.schemas import Project, Ticket, TicketOrderSprint


class TicketBacklogList(Resource):

    def __init__(self):
        super(TicketBacklogList, self).__init__()

    def get(self, project_pk):
        return Ticket.objects(project=project_pk).order_by('order').to_json()

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


class TicketOrderBacklogList(Resource):

    def __init__(self):
        super(TicketOrderBacklogList, self).__init__()

    def get(self, project_pk):
        return Ticket.objects(project=project_pk).order_by('order').to_json()

    def post(self, project_pk):
        """
        update backlog order
        """
        data = request.get_json(force=True, silent=True)
        if data:
            for index, s in enumerate(data):
                ticket = Ticket.objects.get(project=project_pk, pk=s)
                ticket.order = index
                ticket.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class TicketSprintList(Resource):

    def __init__(self):
        super(TicketSprintList, self).__init__()

    def get(self, sprint_pk):
        return TicketOrderSprint.objects(sprint=sprint_pk).order_by('order').to_json()

    def post(self, sprint_pk):
        """
        update order
        """
        data = request.get_json(force=True, silent=True)
        if data:
            for index, s in enumerate(data):
                sprint = TicketOrderSprint.objects.get(pk=s)
                sprint.order = index
                sprint.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400