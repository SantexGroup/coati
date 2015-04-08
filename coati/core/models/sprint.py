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
            instances = cls.objects(project=project_pk)
        except cls.DoesNotExtis:
            instances = []
        return instances


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
        try:
            spo = cls.objects(sprint=sprint_pk, ticket=ticket_pk, active=True)
            spo.active = False
            spo.save()
        except cls.DoesNotExits:
            pass




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
    def get_next_order_index(cls, col):
        return cls.objects(column=col).count()