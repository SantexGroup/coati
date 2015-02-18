"""
Helpers for all factories.
BaseFactory
    Base factory model to avoid code repetition.
"""

from factory.mongoengine import MongoEngineFactory


class BaseFactory(MongoEngineFactory):
    """
    Base abstract mongoengine factory model to avoid code repetition.
    """