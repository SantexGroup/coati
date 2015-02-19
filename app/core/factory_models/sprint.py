"""
Sprint factory module.
SprintFactory
    A factory class to create Sprints.
SprintTicketOrderFactory
    A factory class to create Sprint ticket Orders.
"""
from datetime import datetime, timedelta

from app.core.models import sprint
from app.core.factory_models import base, ticket, project

import factory
from factory import fuzzy


__all__ = [
    'SprintFactory',
    'SprintTicketOrderFactory'
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


class SprintTicketOrderFactory(base.BaseFactory):
    """
    Sprint model factory.
    """

    class Meta:
        model = sprint.SprintTicketOrder

    ticket = factory.SubFactory(ticket.TicketFactory)
    ticket_repr = factory.Dict({})
    order = fuzzy.FuzzyInteger(0)
    sprint = factory.SubFactory(SprintFactory)
    active = True
    when = fuzzy.FuzzyDateTime(datetime.now())


