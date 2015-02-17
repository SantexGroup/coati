from bson import json_util
from mongoengine import Q, signals
from app.core import db

from app.core.sprint import Sprint, SprintTicketOrder
from app.core.project_member import ProjectMember
from app.core.ticket import Ticket
from app.core.column import Column, TicketColumnTransition

PROJECT_TYPE = (('S', 'Scrum'),
                ('K', 'Kanban'))


class Project(db.BaseDocument):
    name = db.StringField(required=True, unique_with='owner')
    description = db.StringField()
    active = db.BooleanField(default=True)
    owner = db.ReferenceField('User',
                              reverse_delete_rule=db.CASCADE)
    prefix = db.StringField()
    sprint_duration = db.IntField()
    project_type = db.StringField(max_length=1,
                                  choices=PROJECT_TYPE,
                                  default='S')

    meta = {
        'indexes': ['name']
    }

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        # delete sprints
        Sprint.objects(project=document).delete()
        # delete members
        ProjectMember.objects(project=document).delete()
        # delete tickets
        Ticket.objects(project=document).delete()
        # delete columns
        Column.objects(project=document).delete()

    def to_json(self):
        data = self.to_dict()
        if isinstance(self.project_type, bool) and self.project_type:
            data["project_type"] = 'S'
        elif isinstance(self.project_type, bool) and not self.project_type:
            data["project_type"] = 'K'
        data["owner"] = self.owner.to_dict()
        data["owner"]["id"] = str(self.owner.pk)
        data['members'] = ProjectMember.get_members_for_project(self)
        del data["owner"]["_id"]
        return json_util.dumps(data)

    def clean(self):
        if self.owner is None:
            raise db.ValidationError('Owner must be provided')

    def get_tickets(self):
        tickets = []
        sprints = Sprint.objects(project=self)
        if self.project_type == u'S':
            for s in sprints:
                for spo in SprintTicketOrder.objects(sprint=s, active=True):
                    tickets.append(str(spo.ticket.pk))

        result = Ticket.objects(Q(project=self) &
                                Q(id__nin=tickets) &
                                (Q(closed=False) | Q(closed__exists=False))
        ).order_by('order')

        return result

    def get_tickets_board(self):
        tickets = []
        col_ids = []
        column_list = Column.objects(project=self)
        for c in column_list:
            col_ids.append(str(c.pk))
        tct_list = TicketColumnTransition.objects(column__in=col_ids,
                                                  latest_state=True)
        for t in tct_list:
            tickets.append(str(t.ticket.pk))

        result = Ticket.objects(Q(project=self) &
                                Q(id__nin=tickets) &
                                (Q(closed=False) | Q(
                                    closed__exists=False))).order_by('order')
        return result


signals.pre_delete.connect(Project.pre_delete, sender=Project)