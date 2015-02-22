from app.core import db
from app.core.helpers.sprints import sprint_to_json


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

    def to_json(self, *args, **kwargs):
        return sprint_to_json(self, kwargs.get('archived'))

    def clean(self):
        if self.project is None:
            raise db.ValidationError('Project must be provided')