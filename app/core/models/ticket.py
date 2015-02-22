from app.core import db
from app.core.helpers.tickets import ticket_to_json

TICKET_TYPE = (('U', 'User Story'),
               ('F', 'Feature'),
               ('B', 'Bug'),
               ('I', 'Improvement'),
               ('E', 'Epic'),
               ('T', 'Task'))


class Ticket(db.BaseDocument):
    title = db.StringField(max_length=200, required=True)
    description = db.StringField()
    labels = db.ListField(db.StringField())
    number = db.IntField()
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)
    order = db.IntField()
    points = db.IntField()
    type = db.StringField(max_length=1, choices=TICKET_TYPE)
    files = db.ListField(db.ReferenceField('Attachment'))
    assigned_to = db.ListField(
        db.ReferenceField('ProjectMember'))
    closed = db.BooleanField(default=False)

    def to_json(self):
        return ticket_to_json(self)