"""
Column function and models.
Column
    A Column schema.
"""
from mongoengine import errors
from bson import json_util
from datetime import datetime
from app.core import db
from comment import Comment


class Column(db.BaseDocument):
    """
    Column schema.
    :ivar title: Title of the column (required).
    :ivar max_cards: Number of cards until shows alarm.
    :ivar color_max_cards: color to show in the alarm.
    :ivar project: Project that belongs (required).
    :ivar done_column: Is a done column.
    :ivar order: index number of order for a particular project.
    """
    title = db.StringField(max_length=100, required=True)
    max_cards = db.IntField(default=9999)
    color_max_cards = db.StringField(default='#FF0000')
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)
    done_column = db.BooleanField(default=False)
    order = db.IntField(required=True)

    def clean(self):
        err_dict = {}

        if not self.title:
            err_dict.update({'title': 'Field is required.'})

        if not self.project:
            err_dict.update({'project': 'Field is required.'})

        if err_dict:
            raise errors.ValidationError(errors=err_dict)

    def to_json(self, *args, **kwargs):
        data = self.to_dict()
        ticket_column = TicketColumnTransition.objects(column=self,
                                                       latest_state=True)\
            .order_by('order')
        tickets = []
        for t in ticket_column:
            if not t.ticket.closed:
                assignments = []
                for ass in t.ticket.assigned_to:
                    if ass.__class__.__name__ != 'DBRef':
                        ma = ass.to_dict()
                        ma['member'] = ass.member.to_dict()
                        assignments.append(ma)

                value = {
                    'points': t.ticket.points,
                    'number': t.ticket.number,
                    'order': t.order,
                    'title': t.ticket.title,
                    '_id': t.ticket.id,
                    'who': t.who.to_dict(),
                    'when': t.when,
                    'type': t.ticket.type,
                    'assigned_to': assignments,
                    'badges': {
                        'comments': Comment.objects(ticket=t.ticket).count(),
                        'files': len(t.ticket.files)
                    }
                }

                tickets.append(value)
        data['tickets'] = tickets
        return json_util.dumps(data)

    def clean(self):
        if self.project is None:
            raise db.ValidationError('Project must be provided')


class TicketColumnTransition(db.BaseDocument):
    ticket = db.ReferenceField('Ticket',
                               reverse_delete_rule=db.CASCADE)
    column = db.ReferenceField('Column',
                               reverse_delete_rule=db.CASCADE)
    sprint = db.ReferenceField('Sprint',
                               reverse_delete_rule=db.CASCADE)
    when = db.DateTimeField(default=datetime.now())
    order = db.IntField()
    who = db.ReferenceField('User',
                            reverse_delete_rule=db.NULLIFY)
    latest_state = db.BooleanField(default=True)