from coati.core import db

TICKET_TYPE = (('U', 'User Story'),
               ('F', 'Feature'),
               ('B', 'Bug'),
               ('I', 'Improvement'),
               ('E', 'Epic'),
               ('T', 'Task'))


class Attachment(db.Document):
    name = db.StringField()
    size = db.IntField()
    type = db.StringField()
    data = db.StringField()


class Ticket(db.Document):
    title = db.StringField(max_length=200, required=True)
    description = db.StringField()
    labels = db.ListField(db.StringField())
    number = db.IntField()
    project = db.ReferenceField('Project', reverse_delete_rule=db.CASCADE)
    order = db.IntField()
    points = db.IntField()
    type = db.StringField(max_length=1, choices=TICKET_TYPE)
    files = db.ListField(db.ReferenceField('Attachment'))
    assigned_to = db.ListField(db.ReferenceField('ProjectMember'))
    closed = db.BooleanField(default=False)
    related_tickets = db.ListField(db.ReferenceField('TicketDependency'))


DEPENDENCY_TYPE = (('B', 'Blocked'),
                   ('BB', 'Blocked By'),
                   ('C', 'Cloned'),
                   ('CB', 'Cloned By'),
                   ('D', 'Duplicated'),
                   ('DB', 'Duplicated By'),
                   ('R', 'Related'))


class TicketDependency(db.Document):
    ticket = db.ReferenceField('Ticket')
    type = db.StringField(choices=DEPENDENCY_TYPE, max_length=2)


class Comment(db.Document):
    comment = db.StringField()
    who = db.ReferenceField('User',
                            reverse_delete_rule=db.NULLIFY)
    ticket = db.ReferenceField('Ticket',
                               reverse_delete_rule=db.CASCADE)
