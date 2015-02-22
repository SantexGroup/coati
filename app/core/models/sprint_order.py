from datetime import datetime
from app.core import db
from app.core.models.sprint import Sprint

class SprintTicketOrder(db.BaseDocument):
    ticket = db.ReferenceField('Ticket',
                               reverse_delete_rule=db.CASCADE)
    ticket_repr = db.DictField()
    order = db.IntField()
    sprint = db.ReferenceField(Sprint,
                               reverse_delete_rule=db.CASCADE)
    active = db.BooleanField(default=True)
    when = db.DateTimeField(default=datetime.now())