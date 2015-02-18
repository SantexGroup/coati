"""
Project factory module.
ProjectFactory
    A factory class to create Projects.
ProjectMemberFactory
    A factory class to create ProjectMembers.
"""

from datetime import datetime
from app.core import project
from app.core.factory_models import base, user

import factory
from factory import fuzzy


__all__ = [
    'ProjectFactory',
    'ProjectMemberFactory'
]


class ProjectFactory(base.BaseFactory):
    """
    Project model factory.
    """

    class Meta:
        model = project.Project

    name = factory.Sequence('Prj_{}'.format)
    description = fuzzy.FuzzyText()
    active = True
    owner = factory.SubFactory(user.UserFactory)
    prefix = factory.LazyAttribute(
        lambda o: '{}'.format(
            o.name[3:]
        ).upper())
    sprint_duration = 15
    project_type = fuzzy.FuzzyChoice(project.PROJECT_TYPE.keys())


class ProjectMemberFactory(base.BaseFactory):
    """
    ProjectMember model factory.
    """

    class Meta:
        model = project.ProjectMember

    member = factory.SubFactory(user.UserFactory)
    project = factory.SubFactory(ProjectFactory)
    since = fuzzy.FuzzyDateTime(datetime.now())
    is_owner = False


