"""
Sprint factory module.
SprintFactory
    A factory class to create Sprints.
"""
from datetime import datetime, timedelta

from app.core import sprint
from app.core.factory_models import base, project

import factory
from factory import fuzzy


__all__ = [
    'SprintFactory'
]


class SprintFactory(base.BaseFactory):
    """
    Sprint model factory.
    """

    class Meta:
        model = sprint.Sprint

    name = factory.Sequence('Sprint_{}'.format)
    start_date = fuzzy.FuzzyDateTime(datetime.now())
    end_date = factory.LazyAttribute(
        lambda o: o.start_date + timedelta(days=15)
    )
    project = factory.SubFactory(project.ProjectFactory)
    order = fuzzy.FuzzyInteger(0)
    started = False
    finalized = False
    total_points_when_started = fuzzy.FuzzyInteger(15)


