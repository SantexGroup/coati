from mongoengine import Document, \
    StringField, BooleanField, ReferenceField, IntField, \
    ListField, EmbeddedDocumentField, EmbeddedDocument
from mongoengine_extras.fields import AutoSlugField


class User(Document):
    email = StringField(required=True, unique=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)


class Column(EmbeddedDocument):
    title = StringField(max_length=100, required=True)
    max_cards = IntField()
    min_cards = IntField()


class Project(Document):
    name = StringField(required=True)
    description = StringField(max_length=500)
    private = BooleanField(default=True)
    active = BooleanField(default=True)
    owner = ReferenceField(User, required=True)
    slug = AutoSlugField(populate_from='name')
    columns = ListField(EmbeddedDocumentField(Column))

