from coati.core import db
from coati.core.models.user import User
from coati.core.models.project import Project, Column
from coati.core.models.ticket import Ticket


class Sprint(db.BaseDocument):
    name = db.StringField(max_length=100, required=True)
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    project = db.ReferenceField(Project,
                                reverse_delete_rule=db.CASCADE)
    order = db.IntField(min_value=0)
    started = db.BooleanField(default=False)
    finalized = db.BooleanField(default=False)
    total_points_when_started = db.IntField()

    @classmethod
    def get_by_project(cls, project_pk):
        try:
            instances = cls.objects(project=project_pk).order_by('order')
        except cls.DoesNotExtis:
            instances = []
        return instances

    @classmethod
    def get_by_project_not_finalized(cls, project_pk):
        try:
            instances = cls.objects(project=project_pk,
                                    finalized=False).order_by('order')
        except cls.DoesNotExtis:
            instances = []
        return instances

    @classmethod
    def get_active_sprint(cls, project_pk):
        try:
            instance = cls.objects.get(project=project_pk,
                                       started=True,
                                       finalized=False)
        except cls.DoesNotExtis:
            instance = None
        return instance

    @classmethod
    def get_archived_sprints(cls, project_pk):
        return cls.objects(project=project_pk, finalized=True).order_by('order')


class SprintTicketOrder(db.BaseDocument):
    ticket = db.ReferenceField(Ticket,
                               reverse_delete_rule=db.CASCADE)
    ticket_repr = db.DictField()
    order = db.IntField()
    sprint = db.ReferenceField(Sprint,
                               reverse_delete_rule=db.CASCADE)
    active = db.BooleanField(default=True)

    @classmethod
    def get_active_sprint_ticket(cls, sprint_pk, ticket_pk):
        try:
            spo = cls.objects(sprint=sprint_pk,
                              ticket=ticket_pk,
                              active=True).first()
        except cls.DoesNotExits:
            spo = None
        return spo

    @classmethod
    def get_active_ticket(cls, ticket_pk):
        try:
            spo = cls.objects(ticket=ticket_pk, active=True).first()
        except cls.DoesNotExits:
            spo = None
        return spo

    @classmethod
    def get_active_sprint(cls, sprint_pk):
        try:
            spo = cls.objects(sprint=sprint_pk, active=True)
        except cls.DoesNotExits:
            spo = None
        return spo

    @classmethod
    def get_next_order_index(cls, sprint_pk):
        return cls.objects(sprint=sprint_pk, active=True).count()

    @classmethod
    def inactivate_spo(cls, sprint_pk, ticket_pk):
        cls.objects(sprint=sprint_pk,
                    ticket=ticket_pk,
                    active=True).update_one(set__active=False)

    @classmethod
    def list_spo(cls, sprint_pk, tickets_ids):
        return cls.objects(ticket__nin=tickets_ids,
                           sprint=sprint_pk,
                           active=True)

    @classmethod
    def inactivate_list_spo(cls, sprint_pk, tickets_ids):
        cls.list_spo(sprint_pk, tickets_ids).update(set__active=False)


    @classmethod
    def order_items(cls, ordered_ids, sprint):
        for index, s in enumerate(ordered_ids):
            item = cls.get_active_sprint_ticket(sprint, s)
            if item:
                item.order = index
                item.save()


class TicketColumnTransition(db.BaseDocument):
    ticket = db.ReferenceField(Ticket, reverse_delete_rule=db.CASCADE)
    column = db.ReferenceField(Column, reverse_delete_rule=db.CASCADE)
    sprint = db.ReferenceField(Sprint, reverse_delete_rule=db.CASCADE)
    order = db.IntField()
    who = db.ReferenceField(User, reverse_delete_rule=db.NULLIFY)
    latest_state = db.BooleanField(default=True)

    @classmethod
    def get_latest_transition(cls, ticket_pk, sprint=None, **kwargs):
        filters = dict(ticket=ticket_pk, latest_state=True)
        if sprint:
            filters.update(dict(sprint=sprint))
        filters.update(kwargs)
        return cls.objects(**filters).first()

    @classmethod
    def get_transitions_in_cols(cls, columns_ids):
        return cls.objects(column__in=columns_ids, latest_state=True)

    @classmethod
    def get_transitions_for_sprint(cls, sprint):
        return cls.objects(sprint=sprint, latest_state=True)

    @classmethod
    def get_next_order_index(cls, col):
        return cls.objects(column=col).count()

    @classmethod
    def order_items(cls, ordered_ids, sprint=None, **kwargs):
        for index, s in enumerate(ordered_ids):
            item = cls.get_latest_transition(ticket_pk=s,
                                             sprint=sprint,
                                             **kwargs)
            if item:
                item.order = index
                item.save()

