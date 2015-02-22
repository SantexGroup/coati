from bson import json_util
from mongoengine import Q
from app.core.models.project import ProjectMember
from app.core.models.sprint import Sprint, SprintTicketOrder
from app.core.models.ticket import Ticket
from app.core.models.column import Column, TicketColumnTransition


def project_to_json(prj_instance):
    data = prj_instance.to_dict()
    if isinstance(prj_instance.project_type,
                  bool) and prj_instance.project_type:
        data["project_type"] = 'S'
    elif isinstance(prj_instance.project_type,
                    bool) and not prj_instance.project_type:
        data["project_type"] = 'K'
    data["owner"] = prj_instance.owner.to_dict()
    data["owner"]["id"] = str(prj_instance.owner.pk)
    data['members'] = ProjectMember.get_members_for_project(prj_instance)
    del data["owner"]["_id"]
    return json_util.dumps(data)


def get_tickets(project):
    tickets = []
    sprints = Sprint.objects(project=project)
    if project.project_type == u'S':
        for s in sprints:
            for spo in SprintTicketOrder.objects(sprint=s, active=True):
                tickets.append(str(spo.ticket.pk))

    result = Ticket.objects(Q(project=project) &
                            Q(id__nin=tickets) &
                            (Q(closed=False) | Q(closed__exists=False))
    ).order_by('order')

    return result


def get_tickets_board(project):
    tickets = []
    col_ids = []
    column_list = Column.objects(project=project)
    for c in column_list:
        col_ids.append(str(c.pk))
    tct_list = TicketColumnTransition.objects(column__in=col_ids,
                                              latest_state=True)
    for t in tct_list:
        tickets.append(str(t.ticket.pk))

    result = Ticket.objects(Q(project=project) &
                            Q(id__nin=tickets) &
                            (Q(closed=False) | Q(
                                closed__exists=False))).order_by('order')
    return result