"""
Mongo DB declaration.

db
    Provides access to all the mongonengine functions and classes from
    `mongoengine` and `mongoengine.fields` modules.

BaseDocument
    Base abstract model schema that provides some common columns and methods
    for subclasses.
"""

from bson import json_util
from mongoengine import errors as mongo_errors, fields

from app.core import utils

from flask.ext.mongoengine import MongoEngine, QuerySet


db = MongoEngine()


class CustomEmailField(fields.EmailField):
    """
    Custom EmailField to use our custom email regex at validation.
    """

    def validate(self, value):
        if not utils.EMAIL_REGEX.match(value):
            self.error(utils.INVALID_EMAIL_MSG)
        super(CustomEmailField, self).validate(value)


class CustomQuerySet(QuerySet):
    """
    Custom QuerySet for additional features.
    """

    def to_json(self, *args, **kwargs):
        return [doc.to_dict(*args, **kwargs) for doc in self]


class BaseDocument(db.Document):
    """
    Base abstract model schema that provides some common columns and methods
    for subclasses.

    :ivar created_on: Creation datetime.
    :ivar updated_on: Last modification datetime.
    """

    excluded_fields = []

    meta = {
        'abstract': True,
        'queryset_class': CustomQuerySet
    }

    created_on = db.DateTimeField(
        required=True,
        default=utils.utcnow
    )
    updated_on = db.DateTimeField(
        required=True,
        default=utils.utcnow
    )

    @classmethod
    def get_by_id(cls, obj_id):
        try:
            instance = cls.objects.get(id=obj_id)
        except (mongo_errors.ValidationError, cls.DoesNotExist):
            instance = None

        return instance

    def save(self, *args, **kwargs):
        self.updated_on = utils.utcnow()

        return super(BaseDocument, self).save(*args, **kwargs)

    def to_dict(self):
        """
        Returns SON dict without the excluded fields.
        """
        data = self.to_mongo()
        for f in self.excluded_fields:
            data.pop(f, None)
        return data

    def to_json(self, *args, **kwargs):
        """
        Dumps a Model instance into a JSON without the excluded fields.

        :return: String representing the JSON.
        """
        data = self.to_dict()

        return json_util.dumps(data)

db.BaseDocument = BaseDocument
