"""
Helper to ease use of factory-boy model factories.
"""

import logging

# Make all model factories available
from app.core.factory_models.column import *  # noqa
from app.core.factory_models.project import *  # noqa
from app.core.factory_models.user import *  # noqa
from app.core.factory_models.attachment import *  # noqa


# Silence annoying factory logs
logging.getLogger('factory').setLevel(logging.WARN)