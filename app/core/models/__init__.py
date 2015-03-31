from datetime import datetime
from flask.ext.mongokit import Document


class RootDocument(Document):
    use_autorefs = True
    use_dot_notation = True

    excluded_fields = []

    structure = {
        'created_at': datetime,
        'updated_at': datetime
    }

    def update(self, E=None, **F):
        self.updated_at = datetime.now()
        super(RootDocument, self).update(E, **F)

    def save(self, uuid=False, validate=None, safe=True, *args, **kwargs):
        self.created_at = datetime.now()
        super(RootDocument, self).save(uuid, validate, safe, *args, **kwargs)

    def to_dict(self):
        data = self.items()
        for f in self.excluded_fields:
            if f in data:
                del data[f]
        return data