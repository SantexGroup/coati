from bson import json_util
from datetime import datetime
from mongoengine import Q, signals
from app.core import db

from app.core.models.sprint import Sprint, SprintTicketOrder
from app.core.models.ticket import Ticket
from app.core.models.column import Column, TicketColumnTransition

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


class ProjectMember(db.BaseDocument):
    member = db.ReferenceField('User',
                               reverse_delete_rule=db.CASCADE)
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)
    since = db.DateTimeField(default=datetime.now())
    is_owner = db.BooleanField(default=False)

    def to_json(self, *args, **kwargs):
        data = self.to_dict()
        data['member'] = self.member.to_dict()
        return json_util.dumps(data)

    @classmethod
    def get_projects_for_member(cls, member_pk):
        prj_mem = cls.objects(member=member_pk)
        projects = []
        for pm in prj_mem:
            if pm.project.active:
                projects.append(pm.project.to_dict())
            elif str(pm.project.owner.pk) == member_pk:
                projects.append(pm.project.to_dict())

        return json_util.dumps(projects)

    @classmethod
    def get_members_for_project(cls, project):
        prj_mem = cls.objects(project=project)
        members = []
        for pm in prj_mem:
            val = pm.to_dict()
            val['member'] = pm.member.to_dict()
            members.append(val)
        return members