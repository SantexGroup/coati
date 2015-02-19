"""
Attachment factory module.
AttachmentFactory
    A factory class to create Attachments.
"""


from app.core.models import attachment
from app.core.factory_models import base

import factory
from factory import fuzzy


__all__ = [
    'AttachmentFactory'
]


class AttachmentFactory(base.BaseFactory):
    """
    Attachment model factory.
    """

    class Meta:
        model = attachment.Attachment

    name = factory.Sequence('Picture_{}'.format)
    size = fuzzy.FuzzyInteger(5000)
    type = 'image/jpeg'
    data = fuzzy.FuzzyText(length=10000)

