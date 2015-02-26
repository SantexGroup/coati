from bson import json_util

from mongoengine import DoesNotExist

from app.core import db
import app.core.models.column as column
import app.core.models.comment as comment
import app.core.models.sprint as sprint
import app.core.models.project as project


TICKET_TYPE = (('U', 'User Story'),
               ('F', 'Feature'),
               ('B', 'Bug'),
               ('I', 'Improvement'),
               ('E', 'Epic'),
               ('T', 'Task'))

__all__ = [
    'Ticket',
    'TicketColumnTransition'
]


class Ticket(db.BaseDocument):
    title = db.StringField(max_length=200, required=True)
    description = db.StringField()
    labels = db.ListField(db.StringField())
    number = db.IntField()
    project = db.ReferenceField(project.Project,
                                reverse_delete_rule=db.CASCADE)
    order = db.IntField()
    points = db.IntField()
    type = db.StringField(max_length=1, choices=TICKET_TYPE)
    files = db.ListField(db.ReferenceField('Attachment'))
    assigned_to = db.ListField(db.ReferenceField(project.ProjectMember))
    closed = db.BooleanField(default=False)

    def to_json(self):
        data = self.to_dict()
        data['project'] = self.project.to_dict()
        data['badges'] = {
            'comments': comment.Comment.objects(ticket=self).count(),
            'files': len(self.files)
        }
        files = []
        for f in self.files:
            if f.__class__.__name__ != 'DBRef':
                file_att = f.to_dict()
                files.append(file_att)
        data['files'] = files
        try:
            tt = column.TicketColumnTransition.objects.get(ticket=self,
                                                    latest_state=True)
            if tt is not None:
                data['in_column'] = tt.column.title
        except DoesNotExist:
            pass

        try:
            sp = sprint.SprintTicketOrder.objects.get(ticket=self, active=True)
            if sp is not None:
                if sp.sprint.__class__.__name__ != 'DBRef':
                    data['sprint'] = sp.sprint.to_dict()
        except DoesNotExist:
            pass

        assignments = []
        for ass in self.assigned_to:
            if ass.__class__.__name__ != 'DBRef':
                val = ass.to_dict()
                val['member'] = ass.member.to_dict()
                assignments.append(val)
        data['assigned_to'] = assignments

        return json_util.dumps(data)