"""
Column factory module.
ColumnFactory
    A factory class to create Columns.
"""


from app.core.models import column
from app.core.factory_models import base, project

import factory
from factory import fuzzy


__all__ = [
    'ColumnFactory'
]


class ColumnFactory(base.BaseFactory):
    """
    Column model factory.
    """

    class Meta:
        model = column.Column

    title = factory.Sequence('Title_{}'.format)
    max_cards = fuzzy.FuzzyInteger(10)
    color_max_cards = '#FF0000'
    project = factory.SubFactory(project.ProjectFactory)
    done_column = True
    order = fuzzy.FuzzyInteger(0)


