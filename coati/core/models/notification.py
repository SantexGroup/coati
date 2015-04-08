from coati.core import db


class UserActivity(db.BaseDocument):
    project = db.ReferenceField('Project')
    verb = db.StringField()
    author = db.ReferenceField('User')
    data = db.DictField()
    to = db.ReferenceField('User')


class UserNotification(db.BaseDocument):
    activity = db.ReferenceField('UserActivity', reverse_delete_rule=db.CASCADE)
    user = db.ReferenceField('User')
    viewed = db.BooleanField(default=False)