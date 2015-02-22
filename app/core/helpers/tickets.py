from bson import json_util
from mongoengine import DoesNotExist

from app.core.models.comment import Comment
from app.core.models.column import TicketColumnTransition
from app.core.models.sprint import SprintTicketOrder


def ticket_to_json(ticket_instace):
    data = ticket_instace.to_dict()
    data['project'] = ticket_instace.project.to_dict()
    data['badges'] = {
        'comments': Comment.objects(ticket=ticket_instace).count(),
        'files': len(ticket_instace.files)
    }
    files = []
    for f in ticket_instace.files:
        if f.__class__.__name__ != 'DBRef':
            file_att = f.to_dict()
            files.append(file_att)
    data['files'] = files
    try:
        tt = TicketColumnTransition.objects.get(ticket=ticket_instace,
                                                latest_state=True)
        if tt is not None:
            data['in_column'] = tt.column.title
    except DoesNotExist:
        pass

    try:
        sp = SprintTicketOrder.objects.get(ticket=ticket_instace, active=True)
        if sp is not None:
            if sp.sprint.__class__.__name__ != 'DBRef':
                data['sprint'] = sp.sprint.to_dict()
    except DoesNotExist:
        pass

    assignments = []
    for ass in ticket_instace.assigned_to:
        if ass.__class__.__name__ != 'DBRef':
            val = ass.to_dict()
            val['member'] = ass.member.to_dict()
            assignments.append(val)
    data['assigned_to'] = assignments

    return json_util.dumps(data)