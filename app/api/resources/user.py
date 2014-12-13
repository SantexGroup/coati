from flask import request, jsonify, session

__author__ = 'gastonrobledo'

import json
from flask.ext.restful import Resource
from mongoengine import Q
from app.schemas import User


class UsersList(Resource):
    def __init__(self):
        super(UsersList, self).__init__()

    def get(self, *args, **kwargs):
        return User.objects.all().to_json()


class UserSearch(Resource):
    def __init__(self):
        super(UserSearch, self).__init__()

    def get(self, query, *args, **kwargs):
        users = User.objects(Q(email__istartswith=query) |
                             Q(first_name__istartswith=query) |
                             Q(last_name__istartswith=query))
        data = []
        for u in users:
            val = dict(text=u.email, value=str(u.pk))
            data.append(val)
        return json.dumps(data), 200


class UserInstance(Resource):
    def __init__(self):
        super(UserInstance, self).__init__()

    def get(self, pk, *args, **kwargs):
        return User.objects.get(id=pk).to_json()

    def put(self, pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            user = User.objects.get(pk=pk)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.picture = data.get('picture', user.picture)
            user.email = data.get('email', user.email)
            user.save()
            return user.to_json(), 200
        return jsonify({'error': 'Bad Request'}), 400


class UserLogged(Resource):

    def __init__(self):
        super(UserLogged, self).__init__()

    def get(self, *args, **kwargs):
        if kwargs['user_id']:
            return User.objects.get(pk=kwargs['user_id']['pk']).to_json()
        return jsonify({}), 204
