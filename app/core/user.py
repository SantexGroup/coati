from bson import json_util
from mongoengine import signals
from app.core import db

from app.core.project import Project
from app.core.project_member import ProjectMember
from app.core.comment import Comment


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

