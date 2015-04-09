import base64
import json

from flask.ext.restful import request

from coati.web.api.auth import AuthResource
from coati.core.models.user import User
from coati.core.models.project import Project, ProjectMember, Column
from coati.core.models.ticket import (Ticket, TicketDependency, Attachment,
                                      Comment)
from coati.core.models.sprint import (Sprint, SprintTicketOrder,
                                      TicketColumnTransition as TicketCT)
from coati.utils import save_notification, send_notification_email_async
from coati.web.api import errors as api_errors
from coati.web.api.auth.utils import current_user


class TicketInstance(AuthResource):
    """
    Ticket Resource
    """

    def get(self, project_pk, tkt_id):
        """
        Get a Ticket Instance
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :return: Ticket Resource
        """
        tkt = Ticket.get_by_id(tkt_id)
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        return tkt.to_dict()

    def put(self, project_pk, tkt_id):
        """
        Update Ticket
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :return: updated Ticket Resource
        """
        tkt = Ticket.get_by_id(tkt_id)
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        data = request.get_json(silent=True)

        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        tkt.description = data.get('description', tkt.description)
        tkt.points = data.get('points', tkt.points)
        tkt.title = data.get('title', tkt.title)
        tkt.labels = data.get('labels', tkt.labels)
        tkt.type = data.get('type', tkt.type)
        tkt.closed = data.get('closed', tkt.closed)

        if 'related_tickets_data' in data:
            for tkt_rel_data in data.get('related_tickets_data'):
                tkt_rel = Ticket.get_by_id(tkt_rel_data.get('value'))
                if tkt_rel:
                    rt = TicketDependency()
                    rt.ticket = tkt_rel
                    rt.type = tkt_rel_data.get('type', 'R')
                    rt.save()
                    tkt.related_tickets.append(rt)

        tkt.save()

        if data.get('sprint'):
            sprint = Sprint.get_by_id(data.get('sprint')['pk'])
            if sprint:
                spo = SprintTicketOrder.get_active_sprint_ticket(sprint, tkt)
                if not spo:
                    # remove old data if this already exists
                    spo = SprintTicketOrder(sprint=sprint, ticket=tkt)
                    spo.ticket_repr = tkt.to_dict()
                    spo.order = SprintTicketOrder.get_next_order_index(sprint)
                spo.save()
        else:
            spo = SprintTicketOrder.get_active_ticket(tkt)
            if spo:
                spo.ticket_repr = tkt.to_dict()
                spo.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='update_ticket',
                          data=tkt.to_dict())

        return tkt.to_dict(), 200


    def delete(self, project_pk, tkt_id):
        """
        Delete Ticket Resource
        :param project_pk: Project ID
        :param tkt_id:  Ticket ID
        :return: Nothing
        """
        tkt = Ticket.get_by_id(tkt_id)
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )
        # save activity
        save_notification(project_pk=project_pk,
                          verb='delete_ticket',
                          data=tkt.to_dict())
        tkt.delete()
        return {}, 204


class TicketProjectList(AuthResource):
    """
    Get Tickets List from Project
    """

    def get(self, project_pk):
        prj = Project.get_by_id(project_pk)
        if not prj:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )

        tickets = []
        sprints = Sprint.get_by_project(prj)

        if prj.project_type == u'S':
            for s in sprints:
                spos = SprintTicketOrder.get_active_sprint(s)
                for spo in spos:
                    tickets.append(spo.ticket.id)

        return Ticket.get_tickets_backlog(project_pk, tickets).to_json()

    def post(self, project_pk):
        """
        Create Ticket
        """
        data = request.get_json(silent=True)

        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        project = Project.get_by_id(project_pk)
        if not project:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )

        tkt = Ticket()

        last_tkt = Ticket.get_last_ticket(project_pk)
        tkt.number = last_tkt.number + 1 if last_tkt else 1
        tkt.order = Ticket.get_next_order_index(project_pk)
        tkt.project = project
        tkt.description = data.get('description')
        tkt.points = data.get('points', 0)
        tkt.title = data.get('title')
        tkt.labels = data.get('labels')
        tkt.type = data.get('type', 'U')
        tkt.save()

        if data.get('sprint'):
            # Assign to a sprint
            sprint = Sprint.get_by_id(pk=data.get('sprint')['pk'])
            if sprint:
                spo = SprintTicketOrder(sprint=sprint, ticket=tkt)
                spo.ticket_repr = tkt.to_dict()
                spo.order = SprintTicketOrder.get_next_order_index(sprint)
                spo.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='new_ticket',
                          data=tkt.to_dict())

        return tkt.to_json(), 201


class TicketOrderProject(AuthResource):
    """
    Order Tickets in a Project
    """

    def post(self, project_pk):
        """
        Update Order
        """
        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        for index, tkt_id in enumerate(data):
            tkt_order = Ticket.get_by_id(tkt_id)
            if tkt_order:
                tkt_order.order = index
                tkt_order.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='backlog_order',
                          data=data)

        return data, 200


class TicketOrderSprint(AuthResource):
    """
    Order Tickets in a Sprint
    """

    def post(self, project_pk, sprint_pk):
        """
        Update Order of tickets in sprint

        :param project_pk: Project ID
        :param sprint_pk: Sprint ID
        :return: Order
        """
        data = request.get_json(silent=True)

        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        sprint = Sprint.get_by_id(sprint_pk)
        if not sprint:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        for index, tkt_id in enumerate(data):
            tkt_order = SprintTicketOrder.get_active_sprint_ticket(sprint,
                                                                   tkt_id)
            if tkt_order:
                tkt_order.order = index
                tkt_order.save()
        # save activity
        save_notification(project_pk=project_pk,
                          verb='sprint_ticket_order',
                          data=data)

        return data, 200


class TicketMovement(AuthResource):
    """
    Move Tickets among Backlog and Sprints
    """

    def post(self, project_pk):
        """
        Move Ticket
        :param project_pk: Project ID
        :return:
        """
        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        source = data.get('source')
        destiny = data.get('dest')

        if not source or not destiny:
            raise api_errors.InvalidAPIUsage(
                payload={
                    'source': api_errors.REQUIRED_MSG,
                    'dest': api_errors.REQUIRED_MSG
                }
            )

        if source.get('project_id'):
            # From project to sprint
            sprint = Sprint.get_by_id(destiny.get('sprint_id'))
            if not sprint:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )

            ticket = Ticket.get_by_id(source.get('ticket_id'))
            if not ticket:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )

            tkt_ord_sprint = SprintTicketOrder()
            tkt_ord_sprint.sprint = sprint
            tkt_ord_sprint.ticket = ticket
            tkt_ord_sprint.ticket_repr = ticket.to_dict()
            tkt_ord_sprint.save()

            for index, tkt_id in enumerate(destiny.get('order')):

                tkt_order = SprintTicketOrder.get_active_sprint_ticket(sprint,
                                                                       tkt_id)
                if tkt_order:
                    tkt_order.order = index
                    tkt_order.save()

        elif source.get('sprint_id') and destiny.get('sprint_id'):
            # From sprint to sprint
            sprint = Sprint.get_by_id(destiny.get('sprint_id'))
            if not sprint:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )

            ticket = Ticket.get_by_id(source.get('ticket_id'))
            if not ticket:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )

            tkt_ord_sprint = SprintTicketOrder()
            tkt_ord_sprint.sprint = sprint
            tkt_ord_sprint.ticket = ticket
            tkt_ord_sprint.ticket_repr = ticket.to_dict()
            tkt_ord_sprint.save()

            for index, tkt_id in enumerate(destiny.get('order')):

                tkt_order = SprintTicketOrder.get_active_sprint_ticket(sprint,
                                                                       tkt_id)
                if tkt_order:
                    tkt_order.order = index
                    tkt_order.save()

            SprintTicketOrder.inactivate_spo(sprint, ticket)

        elif source.get('sprint_id') and destiny.get('project_id'):
            # From sprint to backlog
            sprint = Sprint.get_by_id(source.get('sprint_id'))
            if not sprint:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )

            ticket = Ticket.get_by_id(source.get('ticket_id'))
            if not ticket:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )

            SprintTicketOrder.inactivate_spo(sprint, ticket)

            for index, tkt_id in enumerate(destiny.get('order')):
                tkt_order = Ticket.get_by_id(tkt_id)
                if tkt_order:
                    tkt_order.order = index
                    tkt_order.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='ticket_movement',
                          data=data)

        return data, 200


class TicketTransition(AuthResource):
    """
    Move Tickets Among Columns
    """

    def post(self, project_pk):
        """
        Move Ticket to Column or Backlog
        :param project_pk:
        :return:
        """
        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        project = Project.get_by_id(project_pk)
        if not project:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )
        tkt = Ticket.get_by_id(data.get('ticket'))
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )

        if data.get('backlog'):
            latest_tran = TicketCT.get_latest_transition(tkt)
            if latest_tran:
                latest_tran.latest_state = False
                latest_tran.save()

            for index, s in enumerate(data.get('order')):
                sto = SprintTicketOrder.get_active_sprint_ticket(
                    data.get('backlog'),
                    tkt)
                if sto:
                    sto.order = index
                    sto.save()
            # save activity
            save_notification(project_pk=project_pk,
                              verb='ticket_transition',
                              data=data)

        else:
            # Search already state
            col = Column.get_by_id(data.get('column'))

            if not col:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )

            user = User.get_by_id(current_user.id)
            if not user:
                raise api_errors.MissingResource(
                    api_errors.INVALID_USER_MSG
                )

            transition = TicketCT()
            transition.ticket = tkt
            transition.column = col
            transition.order = TicketCT.get_next_order_index(col)

            if project.project_type == 'S':
                sp = data.get('sprint')
                sprint = Sprint.get_by_id(sp)
                if not sprint:
                    raise api_errors.MissingResource(
                        api_errors.INVALID_OBJECT_ID_MSG
                    )
                latest_tran = TicketCT.get_latest_transition(tkt, sprint)

                transition.sprint = sprint
            else:
                latest_tran = TicketCT.get_latest_transition(tkt)

            if latest_tran:
                latest_tran.latest_state = False
                latest_tran.save()

            transition.latest_state = True
            transition.who = user
            transition.save()

            # execute order
            for index, tkt_id in enumerate(data.get('order')):

                if project.project_type == 'S':
                    tkt_trans_order = TicketCT.get_latest_transition(tkt_id,
                                                                     sprint=sp,
                                                                     column=col)
                else:
                    tkt_trans_order = TicketCT.get_latest_transition(tkt_id,
                                                                     column=col)
                if tkt_trans_order:
                    tkt_trans_order.order = index
                    tkt_trans_order.save()

            # save activity
            save_notification(project_pk=project_pk,
                              verb='ticket_transition',
                              data=transition.to_dict())

            return transition.to_json(), 201


class TicketColumnOrder(AuthResource):
    """
    Order Tickets in Columns
    """

    def post(self, project_pk, column):
        """
        Order Tickets in Columns
        :param project_pk: Project ID
        :param column: Column ID
        :return: Order
        """
        data = request.get_json(silent=True)

        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        project = Project.get_by_id(project_pk)
        if not project:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )

        col = Column.get_by_id(column)
        if not col:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        if project.project_type == 'S':
            sprint = Sprint.get_by_id(data.get('sprint'))
            if not sprint:
                raise api_errors.MissingResource(
                    api_errors.INVALID_OBJECT_ID_MSG
                )
        # execute order
        for index, tkt_id in enumerate(data.get('order')):
            if sprint:
                tkt_trans_order = TicketCT.get_latest_transition(tkt_id, sprint)
            else:
                tkt_trans_order = TicketCT.get_latest_transition(tkt_id)
            tkt_trans_order.order = index
            tkt_trans_order.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='ticket_column_order',
                          data=data)
        return data, 200


class CommentInstance(AuthResource):
    """
    Comment Instance
    """

    def get(self, project_pk, tkt_id, comment_id):
        """
        Get a Comment Resource

        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param comment_id: Comment ID
        :return:
        """
        comment = Comment.get_by_id(comment_id)
        if not comment:
            api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        return comment.to_json()

    def put(self, project_pk, tkt_id, comment_id):
        """
        Update a comment
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param comment_id: Comment ID
        :return: Updated Comment
        """
        comment = Comment.get_by_id(comment_id)
        if not comment:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        if comment.who.id != current_user.id:
            raise api_errors.ForbiddenRequest()

        comment.comment = data.get('comment')
        comment.save()

        save_notification(project_pk=project_pk,
                          verb='update_comment',
                          data={
                              "comment": comment.to_dict(),
                              "ticket": comment.ticket.to_dict()
                          })

        return comment.to_dict(), 200

    def delete(self, project_pk, tkt_id, comment_id):
        """
        Delete a Comment
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param comment_id: Comment ID
        :return: Nothing
        """
        comment = Comment.get_by_id(comment_id)
        if not comment:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        if comment.who.id != current_user.id:
            raise api_errors.ForbiddenRequest()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='delete_comment',
                          data={
                              "comment": comment.to_dict(),
                              "ticket": comment.ticket.to_dict()
                          })

        comment.delete()
        return {}, 204


class TicketComments(AuthResource):
    """
    Comment List for a Ticket
    """

    def get(self, project_pk, tkt_id):
        """
        Get the list of comments
        :param project_pk:
        :param tkt_id:
        :return:
        """
        return Comment.get_by_ticket(tkt_id).to_json()

    def post(self, project_pk, tkt_id):
        """
        Create a Comment for a ticket
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :return: Created Comment
        """
        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        c = Comment(ticket=tkt_id)
        c.who = current_user
        c.comment = data.get('comment')
        c.save()

        if data.get('mentions'):
            for m in data.get('mentions'):
                if m is not None:
                    user = User.get_by_id(m)
                    if user:
                        send_notification_email_async(user, c)
                        # save activity
                        save_notification(project_pk=project_pk,
                                          verb='mention',
                                          user_to=user,
                                          data={
                                              "comment": c.to_dict(),
                                              "ticket": c.ticket.to_dict()
                                          })
        else:
            # save activity
            save_notification(project_pk=project_pk,
                              verb='new_comment',
                              data={
                                  "comment": c.to_dict(),
                                  "ticket": c.ticket.to_dict()
                              })

        return c.to_json(), 201


class TicketAttachments(AuthResource):
    """
    Attachments for a Ticket
    """

    def post(self, project_pk, tkt_id):
        """
        Add Attachment to Ticket
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :return: Created Attachment
        """
        file_item = request.files.get('file')
        if not file_item:
            raise api_errors.InvalidAPIUsage(
                payload=dict(file=api_errors.REQUIRED_MSG)
            )
        data = json.loads(request.form.get('data'))
        if not data:
            raise api_errors.InvalidAPIUsage(
                payload=dict(data=api_errors.REQUIRED_MSG)
            )

        ticket = Ticket.get_by_id(tkt_id)

        att = Attachment()
        att.name = data.get('name')
        att.size = data.get('size')
        att.type = data.get('type')
        att.data = base64.b64encode(file_item.stream.read())
        att.save()
        ticket.files.append(att)
        ticket.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='new_attachment',
                          data=att.to_dict())

        return att.to_json(), 200


class AttachmentInstance(AuthResource):
    """
    Attachment Instance
    """

    def get(self, project_pk, tkt_id, att_id):
        """
        Get an Attachment
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param att_id: Attachment ID
        :return: Attachment
        """
        att = Attachment.get_by_id(att_id)
        if not att:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )
        return att.to_json()

    def delete(self, project_pk, tkt_id, att_id):
        """
        Delete an attachment
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param att_id: Attachment ID
        :return: Nothing
        """
        att = Attachment.get_by_id(att_id)
        tkt = Ticket.get_by_id(pk=tkt_id)
        if not att:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        Ticket.remove_attachment(tkt_id, att)

        # save activity
        save_notification(project_pk=project_pk,
                          verb='delete_attachment',
                          data=att.to_dict())

        att.delete()

        return {}, 204


class MemberTicketInstance(AuthResource):
    """
    Assigned Member to a Ticket
    """

    def put(self, project_pk, tkt_id, pm_id):
        """
        Assign a member to a ticket, this will update the ticket
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param member_id: Member ID
        :return: Ticket Object
        """

        tkt = Ticket.get_by_id(tkt_id)
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        pm = ProjectMember.get_by_id(pm_id)
        if not pm:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        if pm in tkt.assigned_to:
            raise api_errors.InvalidAPIUsage()

        tkt.assigned_to.append(pm)
        tkt.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='new_assigment',
                          data=tkt.to_dict())
        return tkt, 200


    def delete(self, project_pk, tkt_id, pm_id):
        """
        Remove member from ticket
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param member_id: ProjectMember ID
        :return: Nothing
        """

        tkt = Ticket.get_by_id(tkt_id)
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        pm = ProjectMember.get_by_id(pm_id)
        if not pm:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        Ticket.remove_member(tkt, pm)

        # save activity
        save_notification(project_pk=project_pk,
                          verb='delete_assignment',
                          data=tkt.to_dict())
        return {}, 204


class TicketSearch(AuthResource):
    """
    Search Tickets Across Projects
    """

    def get(self, query):
        """
        Search Tickets that contains the query
        :param query: text to search
        :return: List of matched tickets
        """
        projects = []
        projects_query = ProjectMember.get_by_member(current_user.id)
        for p in projects_query:
            projects.append(str(p.project.pk))
        return Ticket.search(query, projects).to_json()


class TicketSearchRelated(AuthResource):
    """
    Search Tickets but in One Project
    """

    def get(self, project_pk, query):
        """
        Search Tickets by project

        :param project_pk: Project ID
        :param query: text to search
        :return: List of matched tickets
        """
        prj = Project.get_by_id(project_pk)
        if not prj:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )

        tickets = Ticket.search(query, [str(prj.pk)])
        results = []
        for tkt in tickets:
            val = dict(text='%s-%s: %s' % (tkt.project.prefix,
                                           tkt.number,
                                           tkt.title),
                       value=str(tkt.id))
            results.append(val)
        return results, 200


class TicketClosed(AuthResource):
    """
    Get Tickets Closed
    """

    def get(self, project_pk):
        """
        Get Closed tickets

        :param project_pk: Project ID
        :return: List of tickets closed
        """
        return Ticket.get_closed_tickets(project_pk).to_json()


class TicketBoardProject(AuthResource):
    """
    Get Tickets for board backlog
    """

    def get(self, project_pk):
        """
        Get Tickets for backlog board

        :param project_pk: Project ID
        :return: List of tickets
        """
        tickets = []
        col_ids = []

        prj = Project.get_by_id(project_pk)
        if not prj:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )

        column_list = Column.get_by_project(prj)
        for c in column_list:
            col_ids.append(str(c.pk))

        tct_list = TicketCT.get_transitions_in_cols(col_ids)
        for t in tct_list:
            tickets.append(str(t.ticket.pk))

        results = Ticket.get_tickets_backlog(prj, not_tickets=tickets)
        return results.to_json(), 200


class TicketRelated(AuthResource):
    """
    Related Ticket
    """

    def delete(self, project_pk, tkt_id, rtkt_id):
        """
        Delete Related Ticket
        :param project_pk: Project ID
        :param tkt_id: Ticket ID
        :param rtkt_id: Related Ticket ID
        :return:
        """
        rtkt = TicketDependency.get_by_id(rtkt_id)
        if not rtkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        Ticket.remove_related_ticket(tkt_id, rtkt)
        return {}, 204


class TicketClone(AuthResource):
    """
    Clone Ticket
    """

    def post(self, project_pk, tkt_id):
        """
        Clone Ticket - Make a copy of a ticket
        :param project_pk:
        :param tkt_id:
        :return:
        """
        tkt = Ticket.get_by_id(tkt_id)
        if not tkt:
            raise api_errors.MissingResource(
                api_errors.INVALID_OBJECT_ID_MSG
            )

        prj = Project.get_by_id(project_pk)
        if not prj:
            raise api_errors.MissingResource(
                api_errors.INVALID_PROJECT_MSG
            )

        new_tkt = tkt.clone()
        last_tkt = Ticket.get_last_ticket(prj)
        new_tkt.number = last_tkt.number + 1 if last_tkt else 1
        new_tkt.order = Ticket.get_next_order_index(prj)
        new_tkt.save()
        return new_tkt.to_json(), 200

