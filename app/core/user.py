from bson import json_util
from datetime import datetime
from mongoengine import signals
from app.core import db

from app.core.project import Project, ProjectMember
from app.core.comment import Comment
from app.redis import RedisClient


class User(db.BaseDocument):
    email = db.StringField(required=True)
    password = db.StringField(required=False)
    first_name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)
    activation_token = db.StringField()
    active = db.BooleanField(default=True)
    picture = db.StringField()

    meta = {
        'indexes': [{'fields': ['email'], 'sparse': True, 'unique': True}]
    }

    excluded_fields = ['activation_token', 'password']


    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        # delete projects
        Project.objects(owner=document).delete()
        # delete from project members
        ProjectMember.objects(member=document).delete()
        # delete comment
        Comment.objects(who=document).delete()

    def to_json(self, *args, **kwargs):
        data = self.to_dict()
        return json_util.dumps(data)

# Signals
signals.pre_delete.connect(User.pre_delete, sender=User)


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


class UserNotification(db.BaseDocument):
    activity = db.ReferenceField('UserActivity',
                                 reverse_delete_rule=db.CASCADE)
    user = db.ReferenceField('User')
    viewed = db.BooleanField(default=False)

    def to_json(self):
        data = self.to_dict()
        if self.activity.__class__.__name__ != 'DBRef':
            data['activity'] = self.activity.to_dict()
            data['activity']['project'] = self.activity.project.to_dict()
            data['activity']['author'] = self.activity.author.to_dict()
            data['activity']['data'] = self.activity.data
        return json_util.dumps(data)

