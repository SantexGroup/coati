import base64
from mongoengine import DoesNotExist, GridFSProxy
from app.redis import RedisClient

__author__ = 'gastonrobledo'

from datetime import datetime
from flask import jsonify, session
from flask.ext.restful import Resource, request

from app.schemas import (Project, Ticket, SprintTicketOrder,
                         Sprint, TicketColumnTransition, Column, User, Comment,
                         Attachment)


class TicketInstance(Resource):
    def __init__(self):
        super(TicketInstance, self).__init__()

    def get(self, tkt_id, *args, **kwargs):
        return Ticket.objects.get(pk=tkt_id).to_json()

    def put(self, tkt_id, *args, **kwargs):
        tkt = Ticket.objects.get(pk=tkt_id)
        data = request.get_json(force=True, silent=True)
        if tkt and data:
            tkt.description = data.get('description')
            tkt.points = data.get('points')
            tkt.title = data.get('title')
            tkt.labels = data.get('labels')
            tkt.type = data.get('type')
            tkt.save()

            if data.get('sprint'):
                sprint = Sprint.objects.get(pk=data.get('sprint')['pk'])
                try:
                    spo = SprintTicketOrder.objects.get(sprint=sprint,
                                                        ticket=tkt)
                except DoesNotExist:
                    # remove old data if this already exists
                    spo_old = SprintTicketOrder.objects(ticket=tkt)
                    spo_old.delete()
                    spo = SprintTicketOrder(sprint=sprint, ticket=tkt)
                    spo.order = SprintTicketOrder.objects(sprint=sprint).count()
                spo.save()

            # # add to redis
            r = RedisClient(channel=str(tkt.project.pk))
            r.store('update_ticket', **kwargs)
            return tkt.to_json(), 200
        return jsonify({'error': 'Bad Request'}), 400

    def delete(self, tkt_id, *args, **kwargs):
        tkt = Ticket.objects.get(pk=tkt_id)
        if tkt:
            tkt.delete()
            # # add to redis
            r = RedisClient(channel=str(tkt.project.pk))
            r.store('delete_ticket', **kwargs)
            return jsonify({'success': True}), 200
        return jsonify({'error': 'Bad Request'}), 400


class TicketProjectList(Resource):
    def __init__(self):
        super(TicketProjectList, self).__init__()

    def get(self, project_pk, *args, **kwargs):
        return Project.objects.get(pk=project_pk).get_tickets().to_json()

    def post(self, project_pk, *args, **kwargs):
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
        tkt.project = project
        tkt.description = data.get('description')
        tkt.points = data.get('points')
        tkt.title = data.get('title')
        tkt.labels = data.get('labels')
        tkt.type = data.get('type')
        tkt.save()

        if data.get('sprint'):
            sprint = Sprint.objects.get(pk=data.get('sprint')['pk'])
            spo = SprintTicketOrder(sprint=sprint, ticket=tkt)
            spo.order = SprintTicketOrder.objects(sprint=sprint).count()
            spo.save()

        r = RedisClient(channel=project_pk)
        r.store('new_ticket', **kwargs)

        return tkt.to_json(), 201


class TicketOrderProject(Resource):
    def __init__(self):
        super(TicketOrderProject, self).__init__()

    def post(self, project_pk, *args, **kwargs):
        """
        update backlog order
        """
        data = request.get_json(force=True, silent=True)
        if data:
            for index, tkt_id in enumerate(data):
                tkt_order = Ticket.objects.get(pk=tkt_id,
                                               project=project_pk)
                tkt_order.order = index
                tkt_order.save()
            # add redis
            r = RedisClient(channel=project_pk)
            r.store('backlog_order', **kwargs)
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class TicketOrderSprint(Resource):
    def __init__(self):
        super(TicketOrderSprint, self).__init__()

    def post(self, sprint_pk, *args, **kwargs):
        """
        update order
        """
        data = request.get_json(force=True, silent=True)
        if data:
            sprint = Sprint.objects.get(pk=sprint_pk)
            for index, tkt_id in enumerate(data):
                tkt_order = SprintTicketOrder.objects.get(ticket=tkt_id,
                                                          sprint=sprint)
                tkt_order.order = index
                tkt_order.save()
            # add redis
            r = RedisClient(channel=str(sprint.project.pk))
            r.store('sprint_ticket_order', **kwargs)
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class TicketMovement(Resource):
    def __init__(self):
        super(TicketMovement, self).__init__()

    def post(self, *args, **kwargs):

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
                tkt_ord_sprint.when = datetime.now()
                tkt_ord_sprint.save()

                for index, tkt_id in enumerate(dest.get('order')):
                    try:
                        tkt_order = SprintTicketOrder.objects.get(ticket=tkt_id,
                                                                  sprint=sprint)
                        tkt_order.order = index
                        tkt_order.save()
                    except DoesNotExist:
                        pass

            elif source.get('sprint_id') and dest.get('sprint_id'):
                # From sprint to sprint
                sprint = Sprint.objects.get(pk=dest.get('sprint_id'))
                ticket = Ticket.objects.get(pk=source.get('ticket_id'))
                tkt_ord_sprint = SprintTicketOrder()
                tkt_ord_sprint.sprint = sprint
                tkt_ord_sprint.ticket = ticket
                tkt_ord_sprint.when = datetime.now()
                tkt_ord_sprint.save()

                for index, tkt_id in enumerate(dest.get('order')):
                    tkt_order = SprintTicketOrder.objects.get(ticket=tkt_id,
                                                              sprint=sprint)
                    tkt_order.order = index
                    tkt_order.save()

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
                    tkt_order.save()
            # add redis
            r = RedisClient(channel=str(ticket.project.pk))
            r.store('ticket_movement', **kwargs)
            return jsonify({'success': True}), 200
        return jsonify({'error': 'Bad Request'}), 400


class TicketTransition(Resource):
    def __init__(self):
        super(TicketTransition, self).__init__()

    def post(self, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            if data.get('backlog'):
                tkt = Ticket.objects.get(pk=data.get('ticket'))
                latest_state = TicketColumnTransition.objects(ticket=tkt,
                                                              latest_state=True)
                if latest_state:
                    tct = latest_state[0]
                    tct.latest_state = False
                    tct.save()

                for index, s in enumerate(data.get('order')):
                    sto = SprintTicketOrder.objects.get(
                        sprint=data.get('backlog'),
                        ticket=s)
                    sto.order = index
                    sto.save()
                # add redis
                r = RedisClient(channel=str(tkt.project.pk))
                r.store('ticket_transition', **kwargs)
                return jsonify({'success': True})
            else:
                # Search already state
                tkt = Ticket.objects.get(pk=data.get('ticket'))
                col = Column.objects.get(pk=data.get('column'))
                if tkt and col:

                    latest_state = TicketColumnTransition.objects(ticket=tkt,
                                                                  latest_state=True)
                    if latest_state:
                        tct = latest_state[0]
                        tct.latest_state = False
                        tct.save()

                    transition = TicketColumnTransition()
                    transition.ticket = tkt
                    transition.column = col
                    transition.order = TicketColumnTransition.objects(
                        column=col).count()
                    transition.latest_state = True
                    transition.when = datetime.now()
                    transition.who = User.objects.get(
                        pk=kwargs['user_id']['pk'])
                    transition.save()

                    # execute order
                    for index, tkt_id in enumerate(data.get('order')):
                        tkt_trans_order = TicketColumnTransition.objects.get(
                            ticket=tkt_id,
                            column=col,
                            latest_state=True)
                        tkt_trans_order.order = index
                        tkt_trans_order.save()

                    # add redis
                    r = RedisClient(channel=str(tkt.project.pk))
                    r.store('ticket_transition', **kwargs)
                    return transition.to_json(), 201
                else:
                    return jsonify({'error': 'Bad Request'}), 400
        return jsonify({'error': 'Bad Request'}), 400


class TicketColumnOrder(Resource):
    def __init__(self):
        super(TicketColumnOrder, self).__init__()

    def post(self, column, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            # Search already state
            col = Column.objects.get(pk=column)
            if col:
                # execute order
                for index, tkt_id in enumerate(data.get('order')):
                    tkt_trans_order = TicketColumnTransition.objects.get(
                        ticket=tkt_id,
                        column=col,
                        latest_state=True)
                    tkt_trans_order.order = index
                    tkt_trans_order.save()
                # add redis
                r = RedisClient(channel=str(col.project.pk))
                r.store('ticket_colunm_order', **kwargs)
                return jsonify({'success': True}), 200
            else:
                return jsonify({'error': 'Bad Request'}), 400
        return jsonify({'error': 'Bad Request'}), 400


class TicketComments(Resource):
    def __init__(self):
        super(TicketComments, self).__init__()

    def get(self, tkt_id, *args, **kwargs):
        return Comment.objects(ticket=tkt_id).order_by('-when').to_json()

    def post(self, tkt_id, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            c = Comment(ticket=tkt_id)
            c.who = User.objects.get(pk=kwargs['user_id']['pk'])
            c.comment = data.get('comment')
            c.when = datetime.now()
            c.save()
            # add redis
            r = RedisClient(channel=str(c.ticket.project.pk))
            r.store('new_comment', **kwargs)
            return c.to_json(), 201
        return jsonify({'error': 'Bad Request'}), 400


class TicketAttachments(Resource):
    def __init__(self):
        super(TicketAttachments, self).__init__()

    def get(self, tkt_id, *args, **kwargs):
        pass

    def post(self, tkt_id, *args, **kwargs):
        file_item = request.files.get('file')
        data = request.form
        ticket = Ticket.objects.get(pk=tkt_id)
        if file_item and ticket and data:
            att = Attachment()
            att.name = data.get('name')
            att.size = data.get('size')
            att.type = data.get('type')
            att.data = base64.b64encode(file_item.stream.read())
            att.save()
            ticket.files.append(att)
            ticket.save()
            # add redis
            r = RedisClient(channel=str(ticket.project.pk))
            r.store('new_attachment', **kwargs)
            return att.to_json(), 200

        return jsonify({'error': 'Bad Request'}), 400


class AttachmentInstance(Resource):
    def __init__(self):
        super(AttachmentInstance, self).__init__()

    def get(self, tkt_id, att_id, *args, **kwargs):
        return Attachment.objects.get(pk=att_id).to_json()

    def delete(self, tkt_id, att_id, *args, **kwargs):
        att = Attachment.objects.get(pk=att_id)

        tkt = Ticket.objects.get(pk=tkt_id)
        tkt.update_one(pull__files=att)
        att.delete()
        r = RedisClient(channel=str(tkt.project.pk))
        r.store('delete_attachment', **kwargs)
        return jsonify({}), 204


class MemberTicketInstance(Resource):
    def __init__(self):
        super(MemberTicketInstance, self).__init__()

    def put(self, tkt_id, member_id, *args, **kwargs):
        try:
            tkt = Ticket.objects.get(pk=tkt_id)
            user = User.objects.get(pk=member_id)
            if user not in tkt.assigned_to:
                tkt.assigned_to.append(user)
                tkt.save()
                # add redis
                r = RedisClient(channel=str(tkt.project.pk))
                r.store('new_assigment', **kwargs)
                return jsonify({'success': True}), 200
            return jsonify({'fail': 'Already added'}), 200
        except DoesNotExist as ex:
            return jsonify({'error': 'Bad Request'}), 400

    def delete(self, tkt_id, member_id, *args, **kwargs):
        try:
            tkt = Ticket.objects.get(pk=tkt_id)
            tkt.update_one(pull__assigned_to=member_id)
            r = RedisClient(channel=str(tkt.project.pk))
            r.store('delete_assignment', **kwargs)
            return jsonify({'success': True}), 200
        except DoesNotExist as ex:
            return jsonify({'error': 'Bad Request'}), 400
