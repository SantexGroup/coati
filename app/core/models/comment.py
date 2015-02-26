from datetime import datetime

from bson import json_util

from app.core import db
import app.core.models.user as user
import app.core.models.ticket as ticket


__all__ = [
    'Comment'
]


class Comment(db.BaseDocument):
    comment = db.StringField()
    who = db.ReferenceField(user.User,
                            reverse_delete_rule=db.NULLIFY)
    ticket = db.ReferenceField(ticket.Ticket,
                               reverse_delete_rule=db.CASCADE)
    when = db.DateTimeField(default=datetime.now())

    def to_json(self):
        data = self.to_dict()
        data['who'] = self.who.to_dict()
        data['ticket'] = self.ticket.to_dict()
        return json_util.dumps(data)

    def clean(self):
        if self.who is None:
            raise db.ValidationError('User must be provided')
        if self.ticket is None:
            raise db.ValidationError('Ticket must be provided')
