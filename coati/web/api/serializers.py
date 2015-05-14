from coati.core.models.notification import UserNotification
from coati.core.models.project import ProjectMember, Project, Column
from coati.core.models.sprint import TicketColumnTransition as TicketCT, \
    SprintTicketOrder, Sprint
from coati.core.models.ticket import Comment, Ticket, Attachment
from coati.core.models.user import User
from coati.web.api import json


def register_serializers():
    """
    Register All Serializers by Model
    :return: Nothing
    """
    json.register(User, user_serializer)
    json.register(Project, project_serializer)
    json.register(ProjectMember, project_member_serializer)
    json.register(Ticket, ticket_serializer)
    json.register(Sprint, sprint_serializer)
    json.register(Column, column_serializer)
    json.register(Comment, comment_serializer)
    json.register(UserNotification, user_notification_serializer)
    json.register(Attachment, attachment_serializer)


def ticket_serializer(tkt):
    """
    Serialize a Ticket
    :param tkt: Ticket Instance
    :return: Ticket Composite
    """
    data = tkt.to_dict()
    data['badges'] = {
        'comments': Comment.get_by_ticket(tkt).count(),
        'files': len(tkt.files)
    }
    files = []
    for f in tkt.files:
        if f.__class__.__name__ != 'DBRef':
            files.append(f)
    data['files'] = files

    tt = TicketCT.get_latest_transition(tkt)
    if tt is not None:
        data['in_column'] = tt.column.title

    sp = SprintTicketOrder.get_active_ticket(tkt)
    if sp is not None:
        if sp.sprint.__class__.__name__ != 'DBRef':
            data['sprint'] = sp.sprint

    assignments = []
    for ass in tkt.assigned_to:
        if ass.__class__.__name__ != 'DBRef':
            val = ass.to_dict()
            if ass.member.__class__.__name__ != 'DBRef':
                val['member'] = ass.member.to_dict()
            assignments.append(val)
    data['assigned_to'] = assignments

    related = []
    for r in tkt.related_tickets:
        if r.__class__.__name__ != 'DBRef':
            rtkt = r.to_dict()
            rtkt['ticket'] = r.ticket
            related.append(rtkt)
    data['related_tickets'] = related
    return data


def user_serializer(user):
    """
    Serialize User Object
    :param user: User Instance
    :return: User Dictionary
    """
    return user.to_dict()


def project_serializer(prj):
    """
    Serialize a Project Object
    :param prj: Project Instance
    :return: Project Composite
    """
    prj_dict = prj.to_dict()
    prj_dict['owner'] = prj.owner.to_dict()

    if isinstance(prj.project_type, bool) and prj.project_type:
        prj_dict["project_type"] = 'S'
    elif isinstance(prj.project_type, bool) and not prj.project_type:
        prj_dict["project_type"] = 'K'
    prj_dict['members'] = ProjectMember.get_members_for_project(prj)
    return prj_dict


def sprint_serializer(obj):
    """
    Serialize Sprint
    :param obj: Sprint Instance
    :return: Sprint Composite
    """
    data = obj.to_dict()
    tickets = list(SprintTicketOrder.get_active_sprint(obj.id))
    ticket_list = []
    tickets.sort(key=lambda x: x.order)
    for t in tickets:
        tkt = t.ticket.to_dict()
        tkt['order'] = t.order
        tkt['badges'] = {
            'comments': Comment.get_by_ticket(t.ticket).count(),
            'files': len(t.ticket.files)
        }
        assignments = []
        for ass in t.ticket.assigned_to:
            if ass.__class__.__name__ != 'DBRef':
                assignments.append(ass)
        tkt['assigned_to'] = assignments
        ticket_list.append(tkt)
    data["tickets"] = ticket_list
    return data


def project_member_serializer(pm):
    """
    Serialize a Project Member Object
    :param prj: Project Instance
    :return: Project Member Composite
    """
    data = pm.to_dict()
    data['member'] = pm.member
    return data


def column_serializer(col):
    """
    Serialize a Column Object
    :param col: Column Object
    :return: Column Composite
    """
    data = col.to_dict()
    ticket_column = TicketCT.get_transitions_in_cols([col.pk]).order_by('order')
    tickets = []
    for t in ticket_column:
        if not t.ticket.closed:
            tickets.append(t.ticket)
    data['tickets'] = tickets
    return data


def comment_serializer(com):
    """
    Comment Serializer
    :param com: Comment Object
    :return: Comment Composite
    """
    data = com.to_dict()
    data['who'] = com.who
    data['ticket'] = com.ticket
    return data


def user_notification_serializer(un):
    """
    Serialize Notifications
    :param un:
    :return:
    """
    data = un.to_dict()
    data['activity'] = un.activity.to_dict()
    data['activity']['project'] = un.activity.project
    data['activity']['author'] = un.activity.author
    data['activity']['data'] = un.activity.data
    return data


def attachment_serializer(att):
    """
    Serialize Attachment
    :param att: Attachment Object
    :return: dictionary
    """
    return att.to_dict()