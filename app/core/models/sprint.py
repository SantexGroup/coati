from datetime import datetime

from app.core import db


class Sprint(db.Document):
    name = db.StringField(max_length=100, required=True)
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)
    order = db.IntField(min_value=0)
    started = db.BooleanField(default=False)
    finalized = db.BooleanField(default=False)
    total_points_when_started = db.IntField()


class SprintTicketOrder(db.Document):
    ticket = db.ReferenceField('Ticket',
                               reverse_delete_rule=db.CASCADE)
    ticket_repr = db.DictField()
    order = db.IntField()
    sprint = db.ReferenceField('Sprint',
                               reverse_delete_rule=db.CASCADE)
    active = db.BooleanField(default=True)


class TicketColumnTransition(db.Document):
    ticket = db.ReferenceField('Ticket', reverse_delete_rule=db.CASCADE)
    column = db.ReferenceField('Column', reverse_delete_rule=db.CASCADE)
    sprint = db.ReferenceField('Sprint', reverse_delete_rule=db.CASCADE)
    order = db.IntField()
    who = db.ReferenceField('User', reverse_delete_rule=db.NULLIFY)
    latest_state = db.BooleanField(default=True)