from datetime import datetime, timedelta

import mongoengine
from mongoengine import Q, signals
from bson import json_util


TICKET_TYPE = (('U', 'User Story'),
               ('F', 'Feature'),
               ('B', 'Bug'),
               ('I', 'Improvement'),
               ('E', 'Epic'),
               ('T', 'Task'))


class CustomQuerySet(mongoengine.QuerySet):
    def to_json(self, *args, **kwargs):
        return "[%s]" % (
            ",".join([doc.to_json(*args, **kwargs) for doc in self]))


class User(mongoengine.Document):
    email = mongoengine.StringField(required=True)
    password = mongoengine.StringField(required=False)
    first_name = mongoengine.StringField(max_length=50)
    last_name = mongoengine.StringField(max_length=50)
    activation_token = mongoengine.StringField()
    active = mongoengine.BooleanField(default=True)
    picture = mongoengine.StringField()

    meta = {
        'indexes': [{'fields': ['email'], 'sparse': True, 'unique': True}]
    }


class Token(mongoengine.Document):
    app_token = mongoengine.StringField()
    social_token = mongoengine.StringField()
    provider = mongoengine.StringField()
    user = mongoengine.ReferenceField('User',
                                      reverse_delete_rule=mongoengine.CASCADE)
    expire = mongoengine.DateTimeField()

    @staticmethod
    def verify_token(token):
        try:
            token = Token.objects.get(app_token=token)
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
        token.app_token = kwargs['app_token']
        token.social_token = kwargs['social_token']
        token.provider = kwargs['provider']
        token.expire = datetime.now() + timedelta(seconds=kwargs['expire_in'])
        return token.save()


class Project(mongoengine.Document):
    name = mongoengine.StringField(required=True, unique_with='owner')
    description = mongoengine.StringField(max_length=500)
    active = mongoengine.BooleanField(default=True)
    owner = mongoengine.ReferenceField('User',
                                       reverse_delete_rule=mongoengine.CASCADE)
    prefix = mongoengine.StringField()
    sprint_duration = mongoengine.IntField()
    # true = Scrum, false = Kanban
    project_type = mongoengine.BooleanField(default=True)

    meta = {
        'indexes': ['name'],
        'queryset_class': CustomQuerySet
    }

    def to_json(self):
        data = self.to_mongo()
        data["owner"] = self.owner.to_mongo()
        data["owner"]["id"] = str(self.owner.pk)
        data['members'] = ProjectMember.get_members_for_project(self)
        del data["owner"]["_id"]
        return json_util.dumps(data)

    def clean(self):
        if self.owner is None:
            raise mongoengine.ValidationError('Owner must be provided')

    def get_tickets(self):
        tickets = []
        sprints = Sprint.objects(project=self)
        for s in sprints:
            for spo in SprintTicketOrder.objects(sprint=s, active=True):
                tickets.append(str(spo.ticket.pk))
        result = Ticket.objects(Q(project=self) &
                                Q(id__nin=tickets) &
                                (Q(closed=False) | Q(closed__exists=False))
        ).order_by('order')
        return result


class Sprint(mongoengine.Document):
    name = mongoengine.StringField(max_length=100, required=True)
    start_date = mongoengine.DateTimeField()
    end_date = mongoengine.DateTimeField()
    project = mongoengine.ReferenceField('Project',
                                         reverse_delete_rule=mongoengine.CASCADE)
    order = mongoengine.IntField(min_value=0)
    started = mongoengine.BooleanField(default=False)
    finalized = mongoengine.BooleanField(default=False)
    total_points_when_started = mongoengine.IntField()

    meta = {
        'queryset_class': CustomQuerySet
    }

    def to_json(self, *args, **kwargs):
        data = self.to_mongo()
        if kwargs.get('archived'):
            tickets = SprintTicketOrder.objects(sprint=self.pk).order_by(
                'order')
        else:
            tickets = SprintTicketOrder.objects(sprint=self.pk,
                                                active=True).order_by('order')
        ticket_list = []
        for t in tickets:
            tkt = t.ticket.to_mongo()
            tkt['order'] = t.order
            assignments = []
            for ass in t.ticket.assigned_to:
                if ass.__class__.__name__ != 'DBRef':
                    assignments.append(ass.to_mongo())
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
                    assignments.append(ass.to_mongo())

            value = {
                'points': t.ticket.points,
                'title': '%s-%s: %s' % (t.ticket.project.prefix,
                                        t.ticket.number,
                                        t.ticket.title),
                '_id': t.ticket.id,
                'type': t.ticket.type,
                'added_after': t.when > self.start_date
            }
            try:
                tt = TicketColumnTransition.objects.get(ticket=t.ticket,
                                                        latest_state=True)
                value['who'] = tt.who.to_mongo()
                value['when'] = tt.when
                if tt.column.done_column:
                    value['finished'] = True
                else:
                    value['finished'] = False
            except mongoengine.DoesNotExist:
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
                tkt = t.ticket.to_mongo()
                tkt.order = t.order
                assignments = []
                for ass in t.ticket.assigned_to:
                    if ass.__class__.__name__ != 'DBRef':
                        assignments.append(ass.to_mongo())
                tkt['assigned_to'] = assignments
                ticket_list.append(tkt)
        return json_util.dumps(ticket_list)

    def clean(self):
        if self.project is None:
            raise mongoengine.ValidationError('Project must be provided')


class Attachment(mongoengine.Document):
    name = mongoengine.StringField()
    size = mongoengine.IntField()
    type = mongoengine.StringField()
    data = mongoengine.StringField()


class ProjectMember(mongoengine.Document):
    member = mongoengine.ReferenceField('User',
                                        reverse_delete_rule=mongoengine.CASCADE)
    project = mongoengine.ReferenceField('Project',
                                         reverse_delete_rule=mongoengine.CASCADE)
    since = mongoengine.DateTimeField(default=datetime.now())
    is_owner = mongoengine.BooleanField(default=False)

    meta = {
        'queryset_class': CustomQuerySet
    }

    def to_json(self, *args, **kwargs):
        data = self.to_mongo()
        data['member'] = self.member.to_mongo()
        return json_util.dumps(data)

    @staticmethod
    def get_projects_for_member(member_pk):
        prj_mem = ProjectMember.objects(member=member_pk)
        projects = []
        for pm in prj_mem:
            if pm.project.active:
                projects.append(pm.project.to_mongo())
            elif str(pm.project.owner.pk) == member_pk:
                projects.append(pm.project.to_mongo())

        return json_util.dumps(projects)

    @staticmethod
    def get_members_for_project(project):
        prj_mem = ProjectMember.objects(project=project)
        members = []
        for pm in prj_mem:
            val = pm.to_mongo()
            val['member'] = pm.member.to_mongo()
            members.append(val)
        return members


class Ticket(mongoengine.Document):
    title = mongoengine.StringField(max_length=200, required=True)
    description = mongoengine.StringField()
    labels = mongoengine.ListField(mongoengine.StringField())
    number = mongoengine.IntField()
    project = mongoengine.ReferenceField('Project',
                                         reverse_delete_rule=mongoengine.CASCADE)
    order = mongoengine.IntField()
    points = mongoengine.IntField()
    type = mongoengine.StringField(max_length=1, choices=TICKET_TYPE)
    files = mongoengine.ListField(mongoengine.ReferenceField('Attachment'))
    assigned_to = mongoengine.ListField(
        mongoengine.ReferenceField('ProjectMember'))
    closed = mongoengine.BooleanField(default=False)

    meta = {
        'queryset_class': CustomQuerySet
    }

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        for att in document.files:
            att.delete()


    def to_json(self, *args, **kwargs):
        data = self.to_mongo()
        data['project'] = self.project.to_mongo()
        files = []
        for f in self.files:
            if f.__class__.__name__ != 'DBRef':
                file_att = f.to_mongo()
                files.append(file_att)
        data['files'] = files
        try:
            tt = TicketColumnTransition.objects.get(ticket=self,
                                                    latest_state=True)
            if tt is not None:
                data['in_column'] = tt.column.title
        except mongoengine.DoesNotExist:
            pass

        try:
            sp = SprintTicketOrder.objects.get(ticket=self, active=True)
            if sp is not None:
                if sp.sprint.__class__.__name__ != 'DBRef':
                    data['sprint'] = sp.sprint.to_mongo()
        except mongoengine.DoesNotExist:
            pass

        assignments = []
        for ass in self.assigned_to:
            if ass.__class__.__name__ != 'DBRef':
                assignments.append(ass.to_mongo())
        data['assigned_to'] = assignments

        return json_util.dumps(data)


class SprintTicketOrder(mongoengine.Document):
    ticket = mongoengine.ReferenceField('Ticket',
                                        reverse_delete_rule=mongoengine.CASCADE)
    order = mongoengine.IntField()
    sprint = mongoengine.ReferenceField('Sprint',
                                        reverse_delete_rule=mongoengine.CASCADE)
    active = mongoengine.BooleanField(default=True)
    when = mongoengine.DateTimeField(default=datetime.now())


class Comment(mongoengine.Document):
    comment = mongoengine.StringField()
    who = mongoengine.ReferenceField('User',
                                     reverse_delete_rule=mongoengine.NULLIFY)
    ticket = mongoengine.ReferenceField('Ticket',
                                        reverse_delete_rule=mongoengine.CASCADE)
    when = mongoengine.DateTimeField(default=datetime.now())

    meta = {
        'queryset_class': CustomQuerySet
    }

    def to_json(self, *args, **kwargs):
        data = self.to_mongo()
        data['who'] = self.who.to_mongo()
        return json_util.dumps(data)

    def clean(self):
        if self.who is None:
            raise mongoengine.ValidationError('User must be provided')
        if self.ticket is None:
            raise mongoengine.ValidationError('Ticket must be provided')


class Column(mongoengine.Document):
    title = mongoengine.StringField(max_length=100, required=True)
    max_cards = mongoengine.IntField(default=9999)
    color_max_cards = mongoengine.StringField(default='#FF0000')
    project = mongoengine.ReferenceField('Project',
                                         reverse_delete_rule=mongoengine.CASCADE)
    done_column = mongoengine.BooleanField(default=False)
    order = mongoengine.IntField()

    meta = {
        'queryset_class': CustomQuerySet
    }

    def to_json(self, *args, **kwargs):
        data = self.to_mongo()
        ticket_column = TicketColumnTransition.objects(column=self,
                                                       latest_state=True).order_by(
            'order')
        tickets = []
        for t in ticket_column:

            assignments = []
            for ass in t.ticket.assigned_to:
                if ass.__class__.__name__ != 'DBRef':
                    assignments.append(ass.to_mongo())

            value = {
                'points': t.ticket.points,
                'number': t.ticket.number,
                'order': t.order,
                'title': t.ticket.title,
                '_id': t.ticket.id,
                'who': t.who.to_mongo(),
                'when': t.when,
                'type': t.ticket.type,
                'assigned_to': assignments
            }
            tickets.append(value)
        data['tickets'] = tickets
        return json_util.dumps(data)

    def clean(self):
        if self.project is None:
            raise mongoengine.ValidationError('Project must be provided')


class TicketColumnTransition(mongoengine.Document):
    ticket = mongoengine.ReferenceField('Ticket',
                                        reverse_delete_rule=mongoengine.CASCADE)
    column = mongoengine.ReferenceField('Column',
                                        reverse_delete_rule=mongoengine.CASCADE)
    sprint = mongoengine.ReferenceField('Sprint',
                                        reverse_delete_rule=mongoengine.CASCADE)
    when = mongoengine.DateTimeField(default=datetime.now())
    order = mongoengine.IntField()
    who = mongoengine.ReferenceField('User',
                                     reverse_delete_rule=mongoengine.NULLIFY)
    latest_state = mongoengine.BooleanField(default=True)


class Notification(mongoengine.Document):
    name = mongoengine.StringField()
    to = mongoengine.ReferenceField('User',
                                    reverse_delete_rule=mongoengine.CASCADE)
    message = mongoengine.StringField()
    read = mongoengine.BooleanField(default=False)

    meta = {
        'queryset_class': CustomQuerySet
    }


# Signals

signals.pre_delete.connect(Ticket.pre_delete, sender=Ticket)