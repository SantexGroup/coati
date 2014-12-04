__author__ = 'gastonrobledo'

from flask import jsonify
from flask.ext.restful import Resource, request

from app.schemas import Project, Ticket, SprintTicketOrder, Sprint


class TicketInstance(Resource):
    def __init__(self):
        super(TicketInstance, self).__init__()

    def get(self, tkt_id):
        return Ticket.objects.get(pk=tkt_id).to_json()


class TicketProjectList(Resource):
    def __init__(self):
        super(TicketProjectList, self).__init__()

    def get(self, project_pk):
        return Project.objects.get(pk=project_pk).get_tickets().to_json()

    def post(self, project_pk):
        """
        Create or Update Ticket
        """
        data = request.get_json(force=True, silent=True)
        if not data:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400

        try:
            project = Project.objects.get(id=project_pk)
        except Project.DoesNotExist, e:
            return jsonify({"error": 'project does not exist'}), 400

        tkt = Ticket.objects.get(pk=data.get('pk'))
        if not tkt:
            code = 201
            tkt = Ticket()
            try:
                last_tkt = Ticket.objects(project=project).order_by('-number')
                if last_tkt:
                    number = last_tkt[0].number + 1
                else:
                    number = 1
            except Exception as ex:
                number = 1
            tkt.number = number
            tkt.order = Ticket.objects.count()
        else:
            code = 200

        tkt.project = project
        tkt.description = data.get('description')
        tkt.points = data.get('points')
        tkt.title = data.get('title')
        tkt.labels = data.get('labels')
        tkt.type = data.get('type')
        tkt.save()

        return tkt.to_json(), code


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
                tkt_order = Ticket.objects.get(pk=tkt_id,
                                               project=project_pk)
                tkt_order.order = index
                tkt_order.update()
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
                tkt_order.update()
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
                tkt_ord_sprint.ticket = ticket
                tkt_ord_sprint.save()

                for index, tkt_id in enumerate(dest.get('order')):
                    tkt_order = SprintTicketOrder.objects.get(ticket=tkt_id,
                                                              sprint=sprint)
                    tkt_order.order = index
                    tkt_order.update()

            elif source.get('sprint_id') and dest.get('sprint_id'):
                # From sprint to sprint
                sprint = Sprint.objects.get(pk=dest.get('sprint_id'))
                ticket = Ticket.objects.get(pk=source.get('ticket_id'))
                tkt_ord_sprint = SprintTicketOrder()
                tkt_ord_sprint.sprint = sprint
                tkt_ord_sprint.ticket = ticket
                tkt_ord_sprint.save()

                for index, tkt_id in enumerate(dest.get('order')):
                    tkt_order = SprintTicketOrder.objects.get(ticket=tkt_id,
                                                              sprint=sprint)
                    tkt_order.order = index
                    tkt_order.update()

                sto = SprintTicketOrder.objects.get(ticket=ticket,
                                                    sprint=source.get(
                                                        'sprint_id'))
                sto.delete()

            elif source.get('sprint_id') and dest.get('project_id'):
                # From sprint to backlog
                ticket = Ticket.objects.get(pk=source.get('ticket_id'))
                sprint = Sprint.objects.get(pk=source.get('sprint_id'))
                spo = SprintTicketOrder.objects.get(ticket=ticket,
                                                    sprint=sprint)
                spo.delete()

                for index, tkt_id in enumerate(dest.get('order')):
                    tkt_order = Ticket.objects.get(pk=tkt_id)
                    tkt_order.order = index
                    tkt_order.update()

            return jsonify({'success': True}), 200
        return jsonify({'error': 'Bad Request'}), 400