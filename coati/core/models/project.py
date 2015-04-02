from datetime import datetime

from coati.core import db

PROJECT_TYPE = (('S', 'Scrum'),
                ('K', 'Kanban'))


class Project(db.Document):
    name = db.StringField(required=True, unique_with='owner')
    description = db.StringField()
    active = db.BooleanField(default=True)
    owner = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    prefix = db.StringField()
    sprint_duration = db.IntField()
    project_type = db.StringField(max_length=1,
                                  choices=PROJECT_TYPE,
                                  default='S')

    meta = {
        'indexes': ['name']
    }


class ProjectMember(db.Document):
    member = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    project = db.ReferenceField('Project', reverse_delete_rule=db.CASCADE)
    is_owner = db.BooleanField(default=False)


class Column(db.Document):
    title = db.StringField(max_length=100, required=True)
    max_cards = db.IntField(default=9999)
    color_max_cards = db.StringField(default='#FF0000')
    project = db.ReferenceField('Project', reverse_delete_rule=db.CASCADE)
    done_column = db.BooleanField(default=False)
    order = db.IntField()