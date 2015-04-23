from mongoengine import signals
from coati.core.models.notification import UserNotification, UserActivity
from coati.core.models.project import Project, ProjectMember, Column
from coati.core.models.sprint import Sprint, SprintTicketOrder, \
    TicketColumnTransition
from coati.core.models.ticket import Comment, Ticket
from coati.core.models.user import User
from coati.core.redis import RedisClient


def register_signals():
    # Signals
    signals.post_save.connect(activity_post_save, sender=UserActivity)
    signals.pre_delete.connect(project_pre_delete, sender=Project)
    signals.pre_delete.connect(sprint_pre_delete, sender=Sprint)
    signals.pre_delete.connect(project_member_pre_delete, sender=ProjectMember)
    signals.pre_delete.connect(user_pre_delete, sender=User)
    signals.pre_delete.connect(ticket_pre_delete, sender=Ticket)


def user_pre_delete(sender, document, *args, **kwargs):
    """
    Delete related documents when a User is deleted
    :param sender: Class
    :param document: User Object
    :return: Nothing
    """

    # delete projects
    Project.objects(owner=document).delete()
    # delete from project members
    ProjectMember.objects(member=document).delete()
    # delete comment
    Comment.objects(who=document).delete()


def project_pre_delete(sender, document, *args, **kwargs):
    """
    Delete related documents when a User is deleted
    :param sender: Class
    :param document: Project Object
    :return: Nothing
    """
    # delete sprints
    Sprint.objects(project=document).delete()
    # delete members
    ProjectMember.objects(project=document).delete()
    # delete tickets
    Ticket.objects(project=document).delete()
    # delete columns
    Column.objects(project=document).delete()


def sprint_pre_delete(sender, document, *args, **kwargs):
    """
    Delete related documents when a User is deleted
    :param sender: Class
    :param document: Sprint Object
    :return: Nothing
    """
    # delete tickets assigned to sprint
    SprintTicketOrder.objects(sprint=document).delete()
    # delete ticket transition
    TicketColumnTransition.objects(sprint=document).delete()


def project_member_pre_delete(sender, document, *args, **kwargs):
    """
    Delete related documents when a Project Member is deleted
    :param sender: Class
    :param document: Project Member Object
    :return: Nothing
    """
    Ticket.objects(
        assigned_to__contains=document
    ).update(pull__assigned_to=document)


def ticket_pre_delete(sender, document, *args, **kwargs):
    """
    Delete related documents when a Ticket is deleted
    :param sender: Class
    :param document: Ticket Object
    :return: Nothing
    """
    # delete attachements
    for att in document.files:
        att.delete()
    # delete ticket column transition
    TicketColumnTransition.objects(ticket=document).delete()
    # delete sprint ticket order
    SprintTicketOrder.objects(ticket=document).delete()
    # delete comments
    Comment.objects(ticket=document).delete()


def activity_post_save(sender, document, *args, **kwargs):
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
            r = RedisClient(channel=str(un.user.pk))
            r.store(document.verb, str(document.author.pk))