__author__ = 'gastonrobledo'

from flask import jsonify
from flask.ext.restful import Resource, request

from app.schemas import Project, Ticket, BacklogTicketOrder, SprintTicketOrder, \
    Sprint


class TicketProjectList(Resource):
    def __init__(self):
        super(TicketProjectList, self).__init__()

    def get(self, project_pk):
        return BacklogTicketOrder.objects(project=project_pk).order_by(
            'order').to_json()

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
            last_tkt = Ticket.objects(project=project).order_by('-number')
            if last_tkt:
                number = last_tkt[0].number + 1
            else:
                number = 1
        except Exception as ex:
            number = 1
        tkt.number = number

        tkt_order = BacklogTicketOrder(ticket=tkt, project=project)
        tkt_order.order = BacklogTicketOrder.objects.count()
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
                tkt_order = SprintTicketOrder.objects.get(ticket=tkt_id,
                                                          sprint=sprint_pk)
                tkt_order.order = index
                tkt_order.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class TicketMovement(Resource):
    def __init__(self):
        super(TicketMovement, self).__init__()

    def post(self):

        data = request.get_json(force=True, silent=True)
        if data:
            source = data['source']
            dest = data['dest']

            if source.get('project_id'):
                # From project to sprint
                sprint = Sprint.objects.get(pk=dest.get('sprint_id'))
                ticket = Ticket.objects.get(pk=source.get('ticket_id'))
                tkt_ord_sprint = SprintTicketOrder()
                tkt_ord_sprint.sprint = sprint
                tkt_ord_sprint.order = SprintTicketOrder.objects.count()
                tkt_ord_sprint.ticket = ticket
                tkt_ord_sprint.save()

                bto = BacklogTicketOrder.objects.get(ticket=ticket,
                                                     project=source.get(
                                                         'project_id'))
                bto.delete()

            elif source.get('sprint_id') and dest.get('sprint_id'):
                # From sprint to sprint
                pass
            elif source.get('sprint_id') and dest.get('project_id'):
                # From sprint to backlog
                pass


            return jsonify({'success': True}), 200
        return jsonify({'error': 'Bad Request'}), 400