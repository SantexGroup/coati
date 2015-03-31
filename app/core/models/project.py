from datetime import datetime

from mongokit import IS

from app.core import db
from app.core.models import RootDocument
from app.core.models.user import User


class Project(RootDocument):
    __collection__ = 'projects'
    structure = {
        'name': unicode,
        'description': unicode,
        'active': bool,
        'owner': User,
        'prefix': unicode,
        'sprint_duration': unicode,
        'proyect_type': IS(u'S', u'K')
    }
    required_fields = ['name', 'owner']
    default_values = {
        'proyect_type': 'S',
        'active': True,
        'sprint_duration': 15
    }
    indexes = [
        {
            'fields': ['name', 'owner'],
            'unique': True
        },
    ]


class ProjectMember(RootDocument):
    __collection__ = 'project_members'
    structure = {
        'member': User,
        'project': Project,
        'since': datetime,
        'is_owner': bool
    }
    required_fields = ['member', 'project', 'since']
    default_values = {
        'since': datetime.now(),
        'is_owner': False
    }

    indexes = [
        {
            'fields': ['member', 'project'],
            'unique': True
        }
    ]


class Column(RootDocument):
    __collection__ = 'columns'
    structure = {
        'project': Project,
        'title': unicode,
        'max_cards': int,
        'color_max_cards': unicode,
        'done_column': bool,
        'order': int
    }
    required_fields = ['project', 'title']
    default_values = {
        'max_cards': 9999,
        'color_max_cards': u'#FF0000',
        'done_column': False,
        'order': 0
    }

    indexes = [
        {
            'fields': ['project', 'title'],
            'unique': True
        }
    ]


db.register([Project, ProjectMember, Column])