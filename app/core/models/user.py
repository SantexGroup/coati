from datetime import datetime
from app.core import db
from app.core.helpers.users import user_notification_to_json


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


class UserActivity(db.BaseDocument):
    project = db.ReferenceField('Project')
    when = db.DateTimeField(default=datetime.now())
    verb = db.StringField()
    author = db.ReferenceField('User')
    data = db.DictField()
    to = db.ReferenceField('User')


class UserNotification(db.BaseDocument):
    activity = db.ReferenceField('UserActivity',
                                 reverse_delete_rule=db.CASCADE)
    user = db.ReferenceField('User')
    viewed = db.BooleanField(default=False)

    def to_json(self):
        return user_notification_to_json(self)

