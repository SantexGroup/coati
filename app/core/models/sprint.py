from datetime import datetime

from app.core import db
from app.core.models import RootDocument
from app.core.models.user import User
from app.core.models.project import Project, Column
from app.core.models.ticket import Ticket


class Sprint(RootDocument):
    __collection__ = 'sprints'
    structure = {
        'name': unicode,
        'start_date': datetime,
        'end_date': datetime,
        'project': Project,
        'order': int,
        'started': bool,
        'finalized': bool,
        'total_points_when_started': int
    }
    required_fields = ['name', 'project']
    default_values = {
        'started': False,
        'finalized': False,
        'order': 0
    }
    indexes = [
        {
            'fields': ['name', 'project'],
            'unique': True,
        },
    ]


class SprintTicket(RootDocument):
    __collection__ = 'sprint_ticket_order'
    structure = {
        'ticket': Ticket,
        'ticket_repr': dict,
        'order': int,
        'sprint': Sprint,
        'active': bool
    }
    required_fields = ['ticket', 'sprint']


class TicketColumnTransition(RootDocument):
    __collection__ = 'ticket_column_transition'
    structure = {
        'ticket': Ticket,
        'column': Column,
        'sprint': Sprint,
        'order': int,
        'who': User,
        'latest_state': bool
    }
    required_fields = ['ticket', 'column', 'sprint', 'who']


db.register([Sprint, SprintTicket, TicketColumnTransition])