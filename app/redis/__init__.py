from flask_redis import Redis
from flask import current_app


class RedisClient():
    def __init__(self):
        self.redis_instance = Redis(current_app)

    def get(self, key):
        return self.redis_instance.get(key)

    def store(self, key, data):
        self.redis_instance.set(key, data)
