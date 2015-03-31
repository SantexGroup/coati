from datetime import datetime
from copy import deepcopy

import mongoengine
from mongoengine import Q, signals
from bson import json_util

from app.redis import RedisClient








class Attachment(CustomDocument):
    name = mongoengine.StringField()
    size = mongoengine.IntField()
    type = mongoengine.StringField()
    data = mongoengine.StringField()
