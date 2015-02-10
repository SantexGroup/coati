"""
Mongo DB declaration.
db
    Provides access to all the mongonengine functions and classes from
    `mongoengine` and `mongoengine.fields` modules.
BaseDocument
    Base abstract model schema that provides some common columns and methods
    for subclasses.
"""

from app.core import utils

from flask.ext.mongoengine import MongoEngine


db = MongoEngine()


class BaseDocument(db.Document):
    """
    Base abstract model schema that provides some common columns and methods
    for subclasses.
    :ivar created_on: Creation datetime.
    :ivar updated_on: Last modification datetime.
    """
    meta = {
        'abstract': True,
    }

    created_on = db.DateTimeField(
        required=True,
        default=utils.utcnow
    )
    updated_on = db.DateTimeField(
        required=True,
        default=utils.utcnow
    )

    def save(self, *args, **kwargs):
        self.updated_on = utils.utcnow()

        return super(BaseDocument, self).save(*args, **kwargs)


db.BaseDocument = BaseDocument