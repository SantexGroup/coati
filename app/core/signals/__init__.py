
from app.core.models.user import UserNotification
from app.core.models.project import ProjectMember, Project
from app.core.models.comment import Comment
from app.core.models.ticket import Ticket
from app.core.models.sprint import SprintTicketOrder, Sprint
from app.core.models.column import Column, TicketColumnTransition


def post_save_user_activity(sender, document, **kwargs):
    from app.redis import RedisClient
    # project notify
    r = RedisClient(channel=str(document.project.pk))
    r.store(document.verb, str(document.author.pk))

    if document.to is not None:
        un = UserNotification(activity=document)
        un.user = document.to
        un.save()
        r = RedisClient(channel=str(un.user.pk))
        r.store(document.verb, str(document.author.pk))
    else:
        pms = ProjectMember.objects(project=document.project)
        for pm in pms:
            un = UserNotification(activity=document)
            un.user = pm.member
            un.save()
            #TODO: Send emails to notify
            r = RedisClient(channel=str(un.user.pk))
            r.store(document.verb, str(document.author.pk))


def pre_delete_user(sender, document, **kwargs):
    # delete projects
    Project.objects(owner=document).delete()
    # delete from project members
    ProjectMember.objects(member=document).delete()
    # delete comment
    Comment.objects(who=document).delete()


def pre_delete_ticket(sender, document, **kwargs):
    # delete attachements
    for att in document.files:
        att.delete()
    # delete ticket column transition
    TicketColumnTransition.objects(ticket=document).delete()
    # delete sprint ticket order
    SprintTicketOrder.objects(ticket=document).delete()
    # delete comments
    Comment.objects(ticket=document).delete()


def pre_delete_sprint(sender, document, **kwargs):
    # delete tickets assigned to sprint
    SprintTicketOrder.objects(sprint=document).delete()
    # delete ticket transition
    TicketColumnTransition.objects(sprint=document).delete()


def pre_delete_project(sender, document, **kwargs):
    # delete sprints
    Sprint.objects(project=document).delete()
    # delete members
    ProjectMember.objects(project=document).delete()
    # delete tickets
    Ticket.objects(project=document).delete()
    # delete columns
    Column.objects(project=document).delete()


def pre_delete_project_member(sender, document, **kwargs):
    Ticket.objects(assigned_to__contains=document).update(
        pull__assigned_to=document)