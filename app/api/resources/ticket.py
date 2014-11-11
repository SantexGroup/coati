__author__ = 'gastonrobledo'

from flask import jsonify
from flask.ext.restful import Resource, request
from app.schemas import Project, Ticket, TicketOrder, Sprint
from mongoengine import queryset


class TicketProjectList(Resource):

    def __init__(self):
        super(TicketProjectList, self).__init__()

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

        tkt = Ticket()
        tkt.description = data.get('description')
        tkt.labels = data.get('labels')
        tkt.title = data.get('title')

        # get max ticket number
        number = 1
        for t in project.tickets:
            if number < t.number:
                number = t.number

        tkt_order = TicketOrder(ticket=tkt)
        tkt_order.order = len(project.tickets)
        tkt_order.number = number + 1

        project.tickets.append(tkt_order)
        tkt.save()
        project.save()

        return tkt.to_json(), 201


class TicketOrderProject(Resource):

    def __init__(self):
        super(TicketOrderProject, self).__init__()

    def post(self, project_pk):
        """
        update backlog order
        """
        data = request.get_json(force=True, silent=True)
        if data:
            project = Project.objects.get(pk=project_pk)
            for index, tkt_id in enumerate(data):
                for tkt_order in project.tickets:
                    if str(tkt_order.ticket.id) == tkt_id:
                        tkt_order.order = index
                        break
            project.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class TicketOrderSprint(Resource):

    def __init__(self):
        super(TicketOrderSprint, self).__init__()


    def post(self, sprint_pk):
        """
        update order
        """
        data = request.get_json(force=True, silent=True)
        if data:
            sprint = Sprint.objects.get(pk=sprint_pk)
            for index, tkt_order in enumerate(sprint.tickets):
                tkt_order.order = index
            sprint.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400