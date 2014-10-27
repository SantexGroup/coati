from mongoengine import Document, \
    StringField, BooleanField, IntField, \
    ListField, EmbeddedDocumentField, EmbeddedDocument, ReferenceField, CASCADE, \
    ValidationError
from mongoengine_extras.fields import slugify, SlugField


class User(Document):
    email = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    meta = {
        'indexes': [{'fields': ['email'], 'sparse': True, 'unique': True}]
    }


class Card(EmbeddedDocument):
    title = StringField(max_length=100, required=True)
    description = StringField(max_length=500)
    labels = ListField(StringField(max_length=50))


class Column(EmbeddedDocument):
    title = StringField(max_length=100, required=True)
    max_cards = IntField()
    min_cards = IntField()
    cards = ListField(EmbeddedDocumentField(Card))


class Project(Document):
    name = StringField(required=True, unique_with='owner')
    description = StringField(max_length=500)
    private = BooleanField(default=True)
    active = BooleanField(default=True)
    owner = ReferenceField(User,
                           dbref=True,
                           reverse_delete_rule=CASCADE)
    columns = ListField(EmbeddedDocumentField(Column))
    slug = SlugField()
    meta = {
        'indexes': ['name', 'slug']
    }

    def clean(self):
        if self.owner is None:
            raise ValidationError('Owner must be provided')
        if self.slug is None:
            self.slug = slugify(self.name)


