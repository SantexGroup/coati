"""
Ticket factory module.
TicketFactory
    A factory class to create Tickets.
"""

from app.core.models import ticket
from app.core.factory_models import base, project

import factory
from factory import fuzzy


__all__ = [
    'TicketFactory'
]


class TicketFactory(base.BaseFactory):
    """
    Ticket model factory.
    """

    class Meta:
        model = ticket.Ticket

    title = factory.Sequence('Titile_{}'.format)
    description = fuzzy.FuzzyText(length=100)
    labels = []
    number = fuzzy.FuzzyInteger(1)
    project = factory.SubFactory(project.ProjectFactory)
    order = fuzzy.FuzzyInteger(0)
    points = fuzzy.FuzzyInteger(1)
    type = fuzzy.FuzzyChoice(ticket.TICKET_TYPE.keys())
    files = factory.List([])
    assigned_to = factory.List([])
    closed = False


