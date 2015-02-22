from bson import json_util
from app.core.models.column import TicketColumnTransition
from app.core.models.comment import Comment


def column_to_json(column):
    data = column.to_dict()
    ticket_column = TicketColumnTransition.objects(column=column,
                                                   latest_state=True) \
        .order_by('order')
    tickets = []
    for t in ticket_column:
        if not t.ticket.closed:
            assignments = []
            for ass in t.ticket.assigned_to:
                if ass.__class__.__name__ != 'DBRef':
                    ma = ass.to_dict()
                    ma['member'] = ass.member.to_dict()
                    assignments.append(ma)

            value = {
                'points': t.ticket.points,
                'number': t.ticket.number,
                'order': t.order,
                'title': t.ticket.title,
                '_id': t.ticket.id,
                'who': t.who.to_dict(),
                'when': t.when,
                'type': t.ticket.type,
                'assigned_to': assignments,
                'badges': {
                    'comments': Comment.objects(ticket=t.ticket).count(),
                    'files': len(t.ticket.files)
                }
            }

            tickets.append(value)
    data['tickets'] = tickets
    return json_util.dumps(data)
