from datetime import datetime
from mongoengine import signals
from app.core import db
from app.redis import RedisClient

from app.core.user import UserNotification
from app.core.project_member import ProjectMember


class UserActivity(db.BaseDocument):
    project = db.ReferenceField('Project')
    when = db.DateTimeField(default=datetime.now())
    verb = db.StringField()
    author = db.ReferenceField('User')
    data = db.DictField()
    to = db.ReferenceField('User')


    @classmethod
    def post_save(cls, sender, document, **kwargs):
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

signals.post_save.connect(UserActivity.post_save, sender=UserActivity)