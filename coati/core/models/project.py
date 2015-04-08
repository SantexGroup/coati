from mongoengine import errors as mongo_errors

from coati.core import db

PROJECT_TYPE = (('S', 'Scrum'),
                ('K', 'Kanban'))


class Project(db.Document):
    name = db.StringField(required=True, unique_with='owner')
    description = db.StringField()
    active = db.BooleanField(default=True)
    owner = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    prefix = db.StringField()
    sprint_duration = db.IntField()
    project_type = db.StringField(max_length=1,
                                  choices=PROJECT_TYPE,
                                  default='S')

    meta = {
        'indexes': ['name']
    }


class ProjectMember(db.Document):
    member = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    project = db.ReferenceField('Project', reverse_delete_rule=db.CASCADE)
    is_owner = db.BooleanField(default=False)

    @classmethod
    def get_by_member(cls, member_id):
        try:
            instances = cls.objects.get(member=member_id)
        except (mongo_errors.ValidationError, cls.DoesNotExist):
            instances = []
        return instances

    @classmethod
    def get_by_project_member(cls, project_pk, member_id):
        return cls.objects(project=project_pk, member=member_id).first()

    @classmethod
    def clear_ownership(cls, project_pk):
        cls.objects(project=project_pk).update(set__is_owner=False)


class Column(db.Document):
    title = db.StringField(max_length=100, required=True)
    max_cards = db.IntField(default=9999)
    color_max_cards = db.StringField(default='#FF0000')
    project = db.ReferenceField('Project', reverse_delete_rule=db.CASCADE)
    done_column = db.BooleanField(default=False)
    order = db.IntField()

    @classmethod
    def get_by_project(cls, project_id):
        try:
            instances = cls.objects(project=project_id).order_by('order')
        except (mongo_errors.ValidationError, cls.DoesNotExist):
            instances = []
        return instances

    @classmethod
    def clear_done_columns(cls, project_id):
        cls.objects(project=project_id).update(set__done_column=False)