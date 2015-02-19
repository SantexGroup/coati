from mongoengine import signals
from bson import json_util
from app.core import db

from column import TicketColumnTransition
from sprint import SprintTicketOrder
from comment import Comment

TICKET_TYPE = (('U', 'User Story'),
               ('F', 'Feature'),
               ('B', 'Bug'),
               ('I', 'Improvement'),
               ('E', 'Epic'),
               ('T', 'Task'))


class Ticket(db.BaseDocument):
    title = db.StringField(max_length=200, required=True)
    description = db.StringField()
    labels = db.ListField(db.StringField())
    number = db.IntField()
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)
    order = db.IntField()
    points = db.IntField()
    type = db.StringField(max_length=1, choices=TICKET_TYPE)
    files = db.ListField(db.ReferenceField('Attachment'))
    assigned_to = db.ListField(
        db.ReferenceField('ProjectMember'))
    closed = db.BooleanField(default=False)

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        # delete attachements
        for att in document.files:
            att.delete()
        # delete ticket column transition
        TicketColumnTransition.objects(ticket=document).delete()
        # delete sprint ticket order
        SprintTicketOrder.objects(ticket=document).delete()
        # delete comments
        Comment.objects(ticket=document).delete()

    def to_json(self):
        data = self.to_dict()
        data['project'] = self.project.to_dict()
        data['badges'] = {
            'comments': Comment.objects(ticket=self).count(),
            'files': len(self.files)
        }
        files = []
        for f in self.files:
            if f.__class__.__name__ != 'DBRef':
                file_att = f.to_dict()
                files.append(file_att)
        data['files'] = files
        try:
            tt = TicketColumnTransition.objects.get(ticket=self,
                                                    latest_state=True)
            if tt is not None:
                data['in_column'] = tt.column.title
        except db.DoesNotExist:
            pass

        try:
            sp = SprintTicketOrder.objects.get(ticket=self, active=True)
            if sp is not None:
                if sp.sprint.__class__.__name__ != 'DBRef':
                    data['sprint'] = sp.sprint.to_dict()
        except db.DoesNotExist:
            pass

        assignments = []
        for ass in self.assigned_to:
            if ass.__class__.__name__ != 'DBRef':
                val = ass.to_dict()
                val['member'] = ass.member.to_dict()
                assignments.append(val)
        data['assigned_to'] = assignments

        return json_util.dumps(data)

signals.pre_delete.connect(Ticket.pre_delete, sender=Ticket)