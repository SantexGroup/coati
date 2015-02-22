from bson import json_util
from mongoengine import DoesNotExist
from app.core.models.sprint_order import SprintTicketOrder
from app.core.models.comment import Comment
from app.core.models.column import TicketColumnTransition, Column


def sprint_to_json(sprint_instance, archived=False):
    data = sprint_instance.to_dict()

    tickets = SprintTicketOrder.objects(sprint=sprint_instance.pk,
                                        active=archived).order_by('order')

    ticket_list = []
    for t in tickets:
        tkt = t.ticket_repr
        tkt['order'] = t.order
        tkt['badges'] = {
            'comments': Comment.objects(ticket=t.ticket).count(),
            'files': len(t.ticket.files)
        }
        assignments = []
        for ass in t.ticket.assigned_to:
            if ass.__class__.__name__ != 'DBRef':
                assignments.append(ass.to_dict())
        tkt['assigned_to'] = assignments
        ticket_list.append(tkt)
    data["tickets"] = ticket_list
    return json_util.dumps(data)


def get_tickets_with_latest_status(sprint_instance):
    tickets = SprintTicketOrder.objects(sprint=sprint_instance).order_by('order')
    result_list = []
    for t in tickets:
        assignments = []
        for ass in t.ticket.assigned_to:
            if ass.__class__.__name__ != 'DBRef':
                assignments.append(ass.to_dict())
        tkt = t.ticket_repr
        value = {
            'points': tkt.get('points'),
            'title': '%s-%s: %s' % (t.ticket.project.prefix,
                                    tkt.get('number'),
                                    tkt.get('title')),
            '_id': t.ticket.id,
            'type': tkt.get('type'),
            'added_after': t.when > sprint_instance.start_date,
            'number': tkt.get('number')
        }
        try:
            tt = TicketColumnTransition.objects.get(ticket=t.ticket,
                                                    latest_state=True)
            value['who'] = tt.who.to_dict()
            value['when'] = tt.when
            value['where'] = tt.column.title
            if tt.column.done_column:
                value['finished'] = True
            else:
                value['finished'] = False
        except DoesNotExist:
            value['finished'] = False

        result_list.append(value)
    return json_util.dumps(result_list)


def get_tickets_board_backlog(sprint_instance):
    # first get all the columns
    columns = Column.objects(project=sprint_instance.project)
    ticket_transitions = TicketColumnTransition.objects(column__in=columns,
                                                        latest_state=True)
    tickets_in_cols = []
    for tt in ticket_transitions:
        tickets_in_cols.append(tt.ticket)

    # exclude from sprint
    tickets = SprintTicketOrder.objects(sprint=sprint_instance,
                                        active=True,
                                        ticket__nin=tickets_in_cols)\
        .order_by('order')
    ticket_list = []
    for t in tickets:
        if t.ticket.__class__.__name__ != 'DBRef':
            tkt = t.ticket_repr
            tkt['order'] = t.order
            tkt['badges'] = {
                'comments': Comment.objects(ticket=t.ticket).count(),
                'files': len(t.ticket.files)
            }
            assignments = []
            for ass in t.ticket.assigned_to:
                if ass.__class__.__name__ != 'DBRef':
                    val = ass.to_dict()
                    val['member'] = ass.member.to_dict()
                    assignments.append(val)
            tkt['assigned_to'] = assignments
            ticket_list.append(tkt)
    return json_util.dumps(ticket_list)