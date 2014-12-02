import mongoengine
from datetime import datetime, timedelta
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


class Token(mongoengine.Document):
    token = mongoengine.StringField()
    provider = mongoengine.StringField()
    user = mongoengine.ReferenceField('User')
    expire = mongoengine.DateTimeField()

    @staticmethod
    def verify_token(token):
        try:
            token = Token.objects.get(token=token)
            if token is None or token.expire <= datetime.now():
                return False
            return True
        except mongoengine.DoesNotExist:
            return False

    @staticmethod
    def get_token_by_user(user_id):
        try:
            return Token.objects.get(user=user_id)
        except mongoengine.DoesNotExist:
            return None

    @staticmethod
    def save_token_for_user(user, **kwargs):
        # remove old tokens
        Token.objects(user=user.to_dbref()).delete()
        # store token in db
        token = Token(user=user.to_dbref())
        token.token = kwargs['access_token']
        token.provider = kwargs['provider']
        token.expire = datetime.now() + timedelta(seconds=kwargs['expire_in'])
        return token.save()


class Ticket(mongoengine.Document):
    title = mongoengine.StringField(max_length=200, required=True)
    description = mongoengine.StringField()
    labels = mongoengine.ListField(mongoengine.StringField())
    number = mongoengine.IntField()
    project = mongoengine.ReferenceField('Project')

    meta = {
        'queryset_class': CustomQuerySet
    }

    def clean(self):
        if not self._created:
            self.number = Ticket.objects(project=self.project).count() + 1


class BacklogTicketOrder(mongoengine.Document):
    ticket = mongoengine.ReferenceField('Ticket')
    order = mongoengine.IntField()
    project = mongoengine.ReferenceField('Project')

    meta = {
        'queryset_class': CustomQuerySet
    }

    def to_json(self, *args, **kwargs):
        data = self.to_mongo()
        data["ticket"] = self.ticket.to_mongo()
        return json_util.dumps(data)


class SprintTicketOrder(mongoengine.Document):
    ticket = mongoengine.ReferenceField('Ticket')
    order = mongoengine.IntField()
    sprint = mongoengine.ReferenceField('Sprint')


class Project(mongoengine.Document):
    name = mongoengine.StringField(required=True, unique_with='owner')
    description = mongoengine.StringField(max_length=500)
    private = mongoengine.BooleanField(default=True)
    active = mongoengine.BooleanField(default=True)
    owner = mongoengine.ReferenceField('User',
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


class Comment(mongoengine.Document):
    comment = mongoengine.StringField()
    who = mongoengine.ReferenceField('User')
    ticket = mongoengine.ReferenceField('Ticket')

    meta = {
        'queryset_class': CustomQuerySet
    }

    def clean(self):
        if self.who is None:
            raise mongoengine.ValidationError('User must be provided')
        if self.ticket is None:
            raise mongoengine.ValidationError('Ticket must be provided')


class Sprint(mongoengine.Document):
    name = mongoengine.StringField(max_length=100, required=True)
    start_date = mongoengine.DateTimeField()
    end_date = mongoengine.DateTimeField()
    project = mongoengine.ReferenceField('Project')
    order = mongoengine.IntField(min_value=0)

    meta = {
        'queryset_class': CustomQuerySet
    }

    def to_json(self):
        data = self.to_mongo()
        tickets = SprintTicketOrder.objects(sprint=self.pk).order_by('order')
        ticket_list = []
        for t in tickets:
            value = {
                'number': t.ticket.number,
                'ticket': t.ticket.to_mongo(),
                '_id': {
                    '$oid': t.id
                }
            }
            ticket_list.append(value)
        data["tickets"] = ticket_list
        return json_util.dumps(data)

    def clean(self):
        if self.project is None:
            raise mongoengine.ValidationError('Project must be provided')


class Column(mongoengine.Document):
    title = mongoengine.StringField(max_length=100, required=True)
    max_cards = mongoengine.IntField()
    min_cards = mongoengine.IntField()
    project = mongoengine.ReferenceField('Project')

    meta = {
        'queryset_class': CustomQuerySet
    }

    def clean(self):
        if self.project is None:
            raise mongoengine.ValidationError('Project must be provided')


class TicketTransition(mongoengine.Document):
    column = mongoengine.ReferenceField('Column')
    ticket = mongoengine.ReferenceField('Ticket')
    date = mongoengine.DateTimeField()
    who = mongoengine.ReferenceField('User')

    meta = {
        'queryset_class': CustomQuerySet
    }

    def clean(self):
        if self.column is None:
            raise mongoengine.ValidationError('Column must be provided')
        if self.ticket is None:
            raise mongoengine.ValidationError('Ticket must be provided')
        if self.who is None:
            raise mongoengine.ValidationError('User must be provided')