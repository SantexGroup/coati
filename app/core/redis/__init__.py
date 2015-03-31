import json
from flask_redis import Redis
from flask import current_app


class RedisClient():
    def __init__(self, channel=None):
        self.channel = channel or 'coati'
        self.redis_instance = Redis(current_app)
        self.pubsub = self.redis_instance.connection.pubsub()
        self.pubsub.subscribe(self.channel)

    def get(self, key):
        return self.redis_instance.get(key)

    def store(self, message_type, author_id):
        data = json.dumps({'type': message_type,
                           'user_id': author_id})
        self.redis_instance.connection.publish(self.channel, data)

