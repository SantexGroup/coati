import mongoengine
from mongoengine_extras.fields import slugify, SlugField
from bson import json_util


class CustomQuerySet(mongoengine.QuerySet):
    def to_json(self):
        return "[%s]" % (",".join([doc.to_json() for doc in self]))


class User(mongoengine.Document):
    email = mongoengine.StringField(required=True)
    first_name = mongoengine.StringField(max_length=50)
    last_name = mongoengine.StringField(max_length=50)
    meta = {
        'indexes': [{'fields': ['email'], 'sparse': True, 'unique': True}]
    }


class Project(mongoengine.Document):
    name = mongoengine.StringField(required=True, unique_with='owner')
    description = mongoengine.StringField(max_length=500)
    private = mongoengine.BooleanField(default=True)
    active = mongoengine.BooleanField(default=True)
    owner = mongoengine.ReferenceField(User,
                                       dbref=True,
                                       reverse_delete_rule=mongoengine.CASCADE)
    prefix = mongoengine.StringField()
    slug = SlugField()

    meta = {
        'indexes': ['name', 'slug'],
        'queryset_class': CustomQuerySet
    }

    def to_json(self):
        data = self.to_mongo()
        data["owner"] = self.owner.to_mongo()
        data["owner"]["id"] = str(self.owner.pk)
        del data["owner"]["_id"]
        return json_util.dumps(data)

    def clean(self):
        if self.owner is None:
            raise mongoengine.ValidationError('Owner must be provided')
        if self.slug is None:
            self.slug = slugify(self.name)


class Ticket(mongoengine.Document):
    title = mongoengine.StringField(max_length=200, required=True)
    description = mongoengine.StringField()
    labels = mongoengine.ListField(mongoengine.StringField())
    project = mongoengine.ReferenceField(Project)
    number = mongoengine.IntField()

    def clean(self):
        try:
            ticket_max = \
            Ticket.objects(project=self.project).order_by('-number').limit(1)[0]
            self.number = ticket_max.number + 1
        except Exception as ex:
            self.number = 1


class Sprint(mongoengine.Document):
    name = mongoengine.StringField(max_length=100, required=True)
    tickets = mongoengine.ListField(mongoengine.ReferenceField(Ticket))
    start_date = mongoengine.DateTimeField(required=True)
    end_date = mongoengine.DateTimeField(required=True)
    project = mongoengine.ReferenceField(Project)


class Column(mongoengine.Document):
    title = mongoengine.StringField(max_length=100, required=True)
    max_cards = mongoengine.IntField()
    min_cards = mongoengine.IntField()
    project = mongoengine.ReferenceField(Project)


class TicketTransition(mongoengine.Document):
    column = mongoengine.ReferenceField(Column)
    ticket = mongoengine.ReferenceField(Ticket)
    date = mongoengine.DateTimeField()
    who = mongoengine.ReferenceField(User)