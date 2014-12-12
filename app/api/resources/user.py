__author__ = 'gastonrobledo'

import json
from flask.ext.restful import Resource
from mongoengine import Q
from app.schemas import User


class UsersList(Resource):
    def __init__(self):
        super(UsersList, self).__init__()

    def get(self):
        return User.objects.all().to_json()


class UserSearch(Resource):
    def __init__(self):
        super(UserSearch, self).__init__()

    def get(self, query):
        users = User.objects(Q(email__istartswith=query) |
                             Q(first_name__istartswith=query) |
                             Q(last_name__istartswith=query))
        data = []
        for u in users:
            val = dict(
                text=u'%s %s (%s)' % (u.first_name, u.last_name, u.email),
                value=str(u.pk))
            data.append(val)
        return json.dumps(data), 200


class UserInstance(Resource):
    def __init__(self):
        super(UserInstance, self).__init__()

    def get(self, pk):
        return User.objects.get(id=pk).to_json()

    def put(self, pk):
        pass