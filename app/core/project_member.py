from datetime import datetime
from bson import json_util
from mongoengine import signals
from app.core import db

from app.core.ticket import Ticket


class ProjectMember(db.BaseDocument):
    member = db.ReferenceField('User',
                               reverse_delete_rule=db.CASCADE)
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)
    since = db.DateTimeField(default=datetime.now())
    is_owner = db.BooleanField(default=False)

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        Ticket.objects(assigned_to__contains=document).update(
            pull__assigned_to=document)

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


signals.pre_delete.connect(ProjectMember.pre_delete, sender=ProjectMember)