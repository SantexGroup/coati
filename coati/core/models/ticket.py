from mongoengine import Q
from coati.core import db

TICKET_TYPE = (('U', 'User Story'),
               ('F', 'Feature'),
               ('B', 'Bug'),
               ('I', 'Improvement'),
               ('E', 'Epic'),
               ('T', 'Task'))


class Attachment(db.BaseDocument):
    name = db.StringField()
    size = db.IntField()
    type = db.StringField()
    data = db.StringField()


class Ticket(db.BaseDocument):
    title = db.StringField(max_length=200, required=True)
    description = db.StringField()
    labels = db.ListField(db.StringField())
    number = db.IntField()
    project = db.ReferenceField('Project', reverse_delete_rule=db.CASCADE)
    order = db.IntField()
    points = db.IntField()
    type = db.StringField(max_length=1, choices=TICKET_TYPE)
    files = db.ListField(db.ReferenceField('Attachment'))
    assigned_to = db.ListField(db.ReferenceField('ProjectMember'))
    closed = db.BooleanField(default=False)
    related_tickets = db.ListField(db.ReferenceField('TicketDependency'))

    @classmethod
    def get_last_ticket(cls, project_pk):
        return cls.objects(project=project_pk).order_by('-number').first()

    @classmethod
    def get_tickets_backlog(cls, project_pk, not_tickets):
        tickets = Ticket.objects(
            Q(project=project_pk) &
            Q(id__nin=not_tickets) &
            (Q(closed=False) | Q(closed__exists=False))).order_by('order')
        return tickets

    @classmethod
    def get_next_order_index(cls, project_pk):
        return cls.objects(project=project_pk).count()

    @classmethod
    def remove_attachment(cls, tkt_id, att):
        cls.objects(pk=tkt_id).update_one(pull__files=att)

    @classmethod
    def remove_member(cls, tkt_id, project_member_id):
        cls.objects(pk=tkt_id).update_one(pull__assigned_to=project_member_id)

    @classmethod
    def remove_related_ticket(cls, tkt_id, related_tkt_id):
        cls.objects(pk=tkt_id).update_one(pull__related_tickets=related_tkt_id)

    @classmethod
    def search(cls, query, projects):
        return cls.objects.distinct((Q(title__icontains=query) |
                                     Q(description__icontains=query)) &
                                    Q(project__in=projects))

    @classmethod
    def get_closed_tickets(cls, project_pk):
        return cls.objects(project=project_pk, closed=True)

    @classmethod
    def close_tickets(cls, tickets_ids):
        cls.objects(pk__in=tickets_ids).update(set__closed=True)


DEPENDENCY_TYPE = (('B', 'Blocked'),
                   ('BB', 'Blocked By'),
                   ('C', 'Cloned'),
                   ('CB', 'Cloned By'),
                   ('D', 'Duplicated'),
                   ('DB', 'Duplicated By'),
                   ('R', 'Related'))


class TicketDependency(db.BaseDocument):
    ticket = db.ReferenceField('Ticket')
    type = db.StringField(choices=DEPENDENCY_TYPE, max_length=2)


class Comment(db.BaseDocument):
    comment = db.StringField()
    who = db.ReferenceField('User',
                            reverse_delete_rule=db.NULLIFY)
    ticket = db.ReferenceField('Ticket',
                               reverse_delete_rule=db.CASCADE)

    @classmethod
    def get_by_ticket(cls, ticket_pk):
        return cls.objects(ticket=ticket_pk).order_by('-created_on')
