from app.core import db
from app.core.models import RootDocument
from app.core.models.user import User
from app.core.models.ticket import Ticket


class Comment(RootDocument):
    __collection__ = 'comments'
    structure = {
        'comment': unicode,
        'author': User,
        'ticket': Ticket
    }
    required_fields = ['comment', 'author', 'ticket']


db.register(Comment)