__author__ = 'gastonrobledo'

from flask import jsonify
from flask.ext.restful import Resource, request

from app.schemas import Project, Ticket, BacklogTicketOrder


class TicketProjectList(Resource):

    def __init__(self):
        super(TicketProjectList, self).__init__()

    def get(self, project_pk):
        return BacklogTicketOrder.objects(project=project_pk).order_by('order').to_json()

    def post(self, project_pk):
        """
        Create Ticket and sort it
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
        try:
            last_tkt = BacklogTicketOrder.objects(project=project).order_by('-number')
            if last_tkt:
                number = last_tkt[0].number + 1
            else:
                number = 1
        except Exception as ex:
            number = 1

        tkt_order = BacklogTicketOrder(ticket=tkt, project=project)
        tkt_order.order = BacklogTicketOrder.objects.count()
        tkt_order.number = number

        tkt.save()
        tkt_order.save()

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
            for index, tkt_id in enumerate(data):
                tkt_order = BacklogTicketOrder.objects.get(ticket=tkt_id,
                                                           project=project_pk)
                tkt_order.order = index
                tkt_order.save()
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
            for index, tkt_id in enumerate(data):
                tkt_order = TicketOrderSprint.objects.get(ticket=tkt_id,
                                                          sprint=sprint_pk)
                tkt_order.order = index
                tkt_order.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400