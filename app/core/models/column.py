"""
Column function and models.
Column
    A Column schema.
"""
from datetime import datetime

from mongoengine import errors

from app.core import db
from app.core.helpers.columns import column_to_json


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
        return column_to_json(self)

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