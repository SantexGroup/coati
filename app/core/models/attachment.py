"""
Attachment function and models.
Attachment
    A Attachment schema.
"""
from mongoengine import errors
from app.core import db

__all__ = [
    'Attachment'
]


class Attachment(db.BaseDocument):
    """
    Attachment schema.
    :ivar name: File's name (required).
    :ivar size: Size in bytes (required).
    :ivar type: mime type of the file.
    :ivar data: Base64 encoded file data (required).
    """
    name = db.StringField(required=True)
    size = db.IntField(required=True)
    type = db.StringField()
    data = db.StringField(required=True)

    def clean(self):
        err_dict = {}

        if not self.name:
            err_dict.update({'name': 'Field is required.'})

        if not self.size:
            err_dict.update({'size': 'Field is required.'})

        if not self.data:
            err_dict.update({'data': 'Field is required.'})

        if err_dict:
            raise errors.ValidationError(errors=err_dict)