from app.core import db
from app.core.models import RootDocument
from app.core.models.user import User
from app.core.models.project import Project


class UserActivity(RootDocument):
    __collection__ = 'user_activity'
    structure = {
        'project': Project,
        'verb': unicode,
        'author': User,
        'data': dict,
        'to': User
    }
    required_fields = ['project', 'verb', 'author', 'data']


class UserNotification(RootDocument):
    __collection__ = 'user_notification'
    structure = {
        'activity': UserActivity,
        'user': User,
        'viewed': bool
    }

    required_fields = ['activity', 'user']

    default_values = {
        'viewed': False
    }


db.register([UserActivity, UserNotification])