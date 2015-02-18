"""
User factory module.
UserFactory
    A factory class to create Users.
"""


from app.core import user
from app.core.factory_models import base

import factory
from factory import fuzzy


__all__ = [
    'UserFactory'
]


class UserFactory(base.BaseFactory):
    """
    User model factory.
    """

    class Meta:
        model = user.User

    password = fuzzy.FuzzyText()
    first_name = factory.Sequence('John_{}'.format)
    last_name = factory.Sequence('Doe_{}'.format)
    activation_token = fuzzy.FuzzyText()
    active = True
    picture = fuzzy.FuzzyText(length=10000)
    email = factory.LazyAttribute(
        lambda o: '{}.{}@example.com'.format(
            o.first_name,
            o.last_name
        ).lower()
    )
