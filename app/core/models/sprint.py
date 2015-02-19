from bson import json_util
from mongoengine import signals
from datetime import datetime
from app.core import db

from app.core.models.column import TicketColumnTransition, Column
from app.core.models.comment import Comment


class Sprint(db.BaseDocument):
    name = db.StringField(max_length=100, required=True)
    start_date = db.DateTimeField()
    end_date = db.DateTimeField()
    project = db.ReferenceField('Project',
                                reverse_delete_rule=db.CASCADE)
    order = db.IntField(min_value=0)
    started = db.BooleanField(default=False)
    finalized = db.BooleanField(default=False)
    total_points_when_started = db.IntField()

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        # delete tickets assigned to sprint
        SprintTicketOrder.objects(sprint=document).delete()
        # delete ticket transition
        TicketColumnTransition.objects(sprint=document).delete()

    def to_json(self, *args, **kwargs):
        data = self.to_dict()
        if kwargs.get('archived'):
            tickets = SprintTicketOrder.objects(sprint=self.pk,
                                                active=False).order_by('order')
        else:
            tickets = SprintTicketOrder.objects(sprint=self.pk,
                                                active=True).order_by('order')
        ticket_list = []
        for t in tickets:
            tkt = t.ticket_repr
            tkt['order'] = t.order
            tkt['badges'] = {
                'comments': Comment.objects(ticket=t.ticket).count(),
                'files': len(t.ticket.files)
            }
            assignments = []
            for ass in t.ticket.assigned_to:
                if ass.__class__.__name__ != 'DBRef':
                    assignments.append(ass.to_dict())
            tkt['assigned_to'] = assignments
            ticket_list.append(tkt)
        data["tickets"] = ticket_list
        return json_util.dumps(data)

    def get_tickets_with_latest_status(self):
        tickets = SprintTicketOrder.objects(sprint=self).order_by('order')
        result_list = []
        for t in tickets:
            assignments = []
            for ass in t.ticket.assigned_to:
                if ass.__class__.__name__ != 'DBRef':
                    assignments.append(ass.to_dict())
            tkt = t.ticket_repr
            value = {
                'points': tkt.get('points'),
                'title': '%s-%s: %s' % (t.ticket.project.prefix,
                                        tkt.get('number'),
                                        tkt.get('title')),
                '_id': t.ticket.id,
                'type': tkt.get('type'),
                'added_after': t.when > self.start_date,
                'number': tkt.get('number')
            }
            try:
                tt = TicketColumnTransition.objects.get(ticket=t.ticket,
                                                        latest_state=True)
                value['who'] = tt.who.to_dict()
                value['when'] = tt.when
                value['where'] = tt.column.title
                if tt.column.done_column:
                    value['finished'] = True
                else:
                    value['finished'] = False
            except db.DoesNotExist:
                value['finished'] = False

            result_list.append(value)
        return json_util.dumps(result_list)

    def get_tickets_board_backlog(self):
        # first get all the columns
        columns = Column.objects(project=self.project)
        ticket_transitions = TicketColumnTransition.objects(column__in=columns,
                                                            latest_state=True)
        tickets_in_cols = []
        for tt in ticket_transitions:
            tickets_in_cols.append(tt.ticket)

        # exclude from sprint
        tickets = SprintTicketOrder.objects(sprint=self,
                                            active=True,
                                            ticket__nin=tickets_in_cols).order_by(
            'order')
        ticket_list = []
        for t in tickets:
            if t.ticket.__class__.__name__ != 'DBRef':
                tkt = t.ticket_repr
                tkt['order'] = t.order
                tkt['badges'] = {
                    'comments': Comment.objects(ticket=t.ticket).count(),
                    'files': len(t.ticket.files)
                }
                assignments = []
                for ass in t.ticket.assigned_to:
                    if ass.__class__.__name__ != 'DBRef':
                        val = ass.to_dict()
                        val['member'] = ass.member.to_dict()
                        assignments.append(val)
                tkt['assigned_to'] = assignments
                ticket_list.append(tkt)
        return json_util.dumps(ticket_list)

    def clean(self):
        if self.project is None:
            raise db.ValidationError('Project must be provided')

signals.pre_delete.connect(Sprint.pre_delete, sender=Sprint)


class SprintTicketOrder(db.BaseDocument):
    ticket = db.ReferenceField('Ticket',
                               reverse_delete_rule=db.CASCADE)
    ticket_repr = db.DictField()
    order = db.IntField()
    sprint = db.ReferenceField('Sprint',
                               reverse_delete_rule=db.CASCADE)
    active = db.BooleanField(default=True)
    when = db.DateTimeField(default=datetime.now())