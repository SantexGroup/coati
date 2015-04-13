from coati.core import db
from coati.core.models.project import Project
from coati.core.models.user import User


def store_notification(user, project, verb, data=None, user_to=None):
    """
    Store a notification
    :param user: User Author
    :param project_pk: Project
    :param verb: Action
    :param data: Data
    :param user_to: Aimed to
    :return: user activity
    """
    prj = Project.get_by_id(project)
    if prj:
        ua = UserActivity()
        ua.project = project
        ua.author = user
        ua.verb = verb
        ua.data = data
        ua.to = user_to
        ua.save()


class UserActivity(db.BaseDocument):
    project = db.ReferenceField(Project)
    verb = db.StringField()
    author = db.ReferenceField(User)
    data = db.DictField()
    to = db.ReferenceField(User)


class UserNotification(db.BaseDocument):
    activity = db.ReferenceField(UserActivity, reverse_delete_rule=db.CASCADE)
    user = db.ReferenceField(User)
    viewed = db.BooleanField(default=False)

