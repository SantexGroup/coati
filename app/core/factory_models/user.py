"""
User factory module.
UserFactory
    A factory class to create Users.
UserActivityFactory
    A factory class to create UserActivities.
"""

from datetime import datetime
from app.core import user
from app.core.factory_models import base, project

import factory
from factory import fuzzy


__all__ = [
    'UserFactory',
    'UserActivityFactory'
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


class UserActivityFactory(base.BaseFactory):
    """
    UserActivityFactory model factory.
    """

    class Meta:
        model = user.UserActivity

    project = factory.SubFactory(project.ProjectFactory)
    when = fuzzy.FuzzyDateTime(datetime.now())
    verb = fuzzy.FuzzyText()
    author = factory.SubFactory(UserFactory)
    data = factory.Dict({})
    to = factory.SubFactory(UserFactory)