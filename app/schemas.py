from datetime import datetime, timedelta

import mongoengine
from mongoengine import Q, signals, queryset_manager
from bson import json_util
from app.redis import RedisClient


TICKET_TYPE = (('U', 'User Story'),
               ('F', 'Feature'),
               ('B', 'Bug'),
               ('I', 'Improvement'),
               ('E', 'Epic'),
               ('T', 'Task'))


class CustomDocument(mongoengine.Document):

    excluded_fields = []

    meta = {
        'abstract': True,
    }

    def to_dict(self):
        data = self.to_mongo()
        for f in self.excluded_fields:
            if data.has_key(f):
                del data[f]
        return data

class CustomQuerySet(mongoengine.QuerySet):
    def to_json(self, *args, **kwargs):
        return "[%s]" % (
            ",".join([doc.to_json(*args, **kwargs) for doc in self]))


class User(CustomDocument):
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

    excluded_fields = ['activation_token', 'password']


    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        # delete tokens
        Token.objects(user=document).delete()
        # delete projects
        Project.objects(owner=document).delete()
        # delete from project members
        ProjectMember.objects(member=document).delete()
        # delete comment
        Comment.objects(who=document).delete()


class Project(CustomDocument):
    name = mongoengine.StringField(required=True, unique_with='owner')
    description = mongoengine.StringField()
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
        data["owner"] = self.owner.to_dict()
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


class Sprint(CustomDocument):
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

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        # delete tickets assigned to sprint
        SprintTicketOrder.objects(sprint=document).delete()
        # delete ticket transition
        TicketColumnTransition.objects(sprint=document).delete()


    def to_json(self, *args, **kwargs):
        data = self.to_dict()
        if kwargs.get('archived'):
            tickets = SprintTicketOrder.objects(sprint=self.pk).order_by(
                'order')
        else:
            tickets = SprintTicketOrder.objects(sprint=self.pk,
                                                active=True).order_by('order')
        ticket_list = []
        for t in tickets:
            tkt = t.ticket.to_dict()
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
                value['who'] = tt.who.to_dict()
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
                tkt = t.ticket.to_dict()
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
            raise mongoengine.ValidationError('Project must be provided')


class Attachment(CustomDocument):
    name = mongoengine.StringField()
    size = mongoengine.IntField()
    type = mongoengine.StringField()
    data = mongoengine.StringField()


class ProjectMember(CustomDocument):
    member = mongoengine.ReferenceField('User',
                                        reverse_delete_rule=mongoengine.CASCADE)
    project = mongoengine.ReferenceField('Project',
                                         reverse_delete_rule=mongoengine.CASCADE)
    since = mongoengine.DateTimeField(default=datetime.now())
    is_owner = mongoengine.BooleanField(default=False)

    meta = {
        'queryset_class': CustomQuerySet
    }

    @classmethod
    def pre_delete(cls, sender, document, **kwargs):
        Ticket.objects(assigned_to__contains=document).update(
            pull__assigned_to=document)

    def to_json(self, *args, **kwargs):
        data = self.to_dict()
        data['member'] = self.member.to_dict()
        return json_util.dumps(data)

    @staticmethod
    def get_projects_for_member(member_pk):
        prj_mem = ProjectMember.objects(member=member_pk)
        projects = []
        for pm in prj_mem:
            if pm.project.active:
                projects.append(pm.project.to_dict())
            elif str(pm.project.owner.pk) == member_pk:
                projects.append(pm.project.to_dict())

        return json_util.dumps(projects)

    @staticmethod
    def get_members_for_project(project):
        prj_mem = ProjectMember.objects(project=project)
        members = []
        for pm in prj_mem:
            val = pm.to_dict()
            val['member'] = pm.member.to_dict()
            members.append(val)
        return members


class Ticket(CustomDocument):
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
        # delete attachements
        for att in document.files:
            att.delete()
        # delete ticket column transition
        TicketColumnTransition.objects(ticket=document).delete()
        # delete sprint ticket order
        SprintTicketOrder.objects(ticket=document).delete()
        # delete comments
        Comment.objects(ticket=document).delete()


    def to_json(self, *args, **kwargs):
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
        except mongoengine.DoesNotExist:
            pass

        try:
            sp = SprintTicketOrder.objects.get(ticket=self, active=True)
            if sp is not None:
                if sp.sprint.__class__.__name__ != 'DBRef':
                    data['sprint'] = sp.sprint.to_dict()
        except mongoengine.DoesNotExist:
            pass

        assignments = []
        for ass in self.assigned_to:
            if ass.__class__.__name__ != 'DBRef':
                val = ass.to_dict()
                val['member'] = ass.member.to_dict()
                assignments.append(val)
        data['assigned_to'] = assignments

        return json_util.dumps(data)


class SprintTicketOrder(CustomDocument):
    ticket = mongoengine.ReferenceField('Ticket',
                                        reverse_delete_rule=mongoengine.CASCADE)
    order = mongoengine.IntField()
    sprint = mongoengine.ReferenceField('Sprint',
                                        reverse_delete_rule=mongoengine.CASCADE)
    active = mongoengine.BooleanField(default=True)
    when = mongoengine.DateTimeField(default=datetime.now())


class Comment(CustomDocument):
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
        data = self.to_dict()
        data['who'] = self.who.to_dict()
        data['ticket'] = self.ticket.to_dict()
        return json_util.dumps(data)

    def clean(self):
        if self.who is None:
            raise mongoengine.ValidationError('User must be provided')
        if self.ticket is None:
            raise mongoengine.ValidationError('Ticket must be provided')


class Column(CustomDocument):
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
        data = self.to_dict()
        ticket_column = TicketColumnTransition.objects(column=self,
                                                       latest_state=True).order_by(
            'order')
        tickets = []
        for t in ticket_column:
            if not t.ticket.closed:
                assignments = []
                for ass in t.ticket.assigned_to:
                    if ass.__class__.__name__ != 'DBRef':
                        ma = ass.to_dict()
                        ma['member'] = ass.member.to_dict()
                        assignments.append(ma)

                value = {
                    'points': t.ticket.points,
                    'number': t.ticket.number,
                    'order': t.order,
                    'title': t.ticket.title,
                    '_id': t.ticket.id,
                    'who': t.who.to_dict(),
                    'when': t.when,
                    'type': t.ticket.type,
                    'assigned_to': assignments,
                    'badges': {
                        'comments': Comment.objects(ticket=t.ticket).count(),
                        'files': len(t.ticket.files)
                    }
                }

                tickets.append(value)
        data['tickets'] = tickets
        return json_util.dumps(data)

    def clean(self):
        if self.project is None:
            raise mongoengine.ValidationError('Project must be provided')


class TicketColumnTransition(CustomDocument):
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


class UserActivity(CustomDocument):
    project = mongoengine.ReferenceField('Project')
    when = mongoengine.DateTimeField(default=datetime.now())
    verb = mongoengine.StringField()
    author = mongoengine.ReferenceField('User')
    data = mongoengine.StringField()
    to = mongoengine.ReferenceField('User')

    meta = {
        'queryset_class': CustomQuerySet
    }


    @classmethod
    def post_save(cls, sender, document, **kwargs):
        # project notify
        r = RedisClient(channel=str(document.project.pk))
        r.store(document.verb, str(document.author.pk))

        if document.to is not None:
            un = UserNotification(activity=document)
            un.user = document.to
            un.save()
            r = RedisClient(channel=str(un.user.pk))
            r.store(document.verb, str(document.author.pk))
        else:
            pms = ProjectMember.objects(project=document.project)
            for pm in pms:
                un = UserNotification(activity=document)
                un.user = pm.member
                un.save()
                r = RedisClient(channel=str(un.user.pk))
                r.store(document.verb, str(document.author.pk))


class UserNotification(CustomDocument):
    activity = mongoengine.ReferenceField('UserActivity',
                                          reverse_delete_rule=mongoengine.CASCADE)
    user = mongoengine.ReferenceField('User')
    viewed = mongoengine.BooleanField(default=False)

    meta = {
        'queryset_class': CustomQuerySet
    }

    def to_json(self, *args, **kwargs):
        data = self.to_dict()
        data['activity'] = self.activity.to_dict()
        data['activity']['project'] = self.activity.project.to_dict()
        author = self.activity.author.to_dict()
        if 'password' in author.keys():
            del author['password']
        if 'activation_token' in author.keys():
            del author['activation_token']
        data['activity']['author'] = author
        data['activity']['data'] = json_util.loads(self.activity.data)
        return json_util.dumps(data)

# Signals
signals.post_save.connect(UserActivity.post_save, sender=UserActivity)
signals.pre_delete.connect(Project.pre_delete, sender=Project)
signals.pre_delete.connect(Sprint.pre_delete, sender=Sprint)
signals.pre_delete.connect(ProjectMember.pre_delete, sender=ProjectMember)
signals.pre_delete.connect(User.pre_delete, sender=User)
signals.pre_delete.connect(Ticket.pre_delete, sender=Ticket)