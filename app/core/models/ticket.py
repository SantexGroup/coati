from mongokit import IS
from app.core import db
from app.core.models import RootDocument
from app.core.models.project import Project, ProjectMember


class Ticket(RootDocument):
    __collection__ = 'tickets'
    structure = {
        'title': unicode,
        'description': unicode,
        'labels': [unicode],
        'number': int,
        'project': Project,
        'order': int,
        'points': int,
        'type': IS(u'U', u'F', u'B', u'I', u'E', u'T'),
        'assigned_to': [ProjectMember],
        'closed': bool,
        'related_tickets': [TicketDependency],
    }
    gridfs = {
        'containers': ['attachments']
    }
    required_fields = ['title', 'project']
    default_values = {
        'type': u'U',
        'closed': False,
        'order': 0,
        'number': 1,
        'points': 0
    }
    indexes = [
        {
            'fields': 'title'
        },
    ]


class TicketDependency(RootDocument):
    __collection__ = 'related_tickets'
    structure = {
        'ticket': Ticket,
        'type': IS(u'B', u'BB', u'C', u'CB', u'D', u'DB', u'R')
    }

    required_fields = ['ticket']


db.register([Ticket, TicketDependency])