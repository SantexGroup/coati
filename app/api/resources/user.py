import json
import hashlib

from flask import request, jsonify
from flask.ext.restful import Resource
from mongoengine import Q, DoesNotExist

from app.api.resources.auth_resource import AuthResource
from app.auth import generate_token
from app.schemas import User, Token, UserNotification
from app.utils import send_activation_email_async


class UsersList(AuthResource):
    def __init__(self):
        super(UsersList, self).__init__()

    def get(self, *args, **kwargs):
        return User.objects.all().to_json()


class UserSearch(AuthResource):
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


class UserInstance(AuthResource):
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


class UserLogged(AuthResource):

    def __init__(self):
        super(UserLogged, self).__init__()

    def get(self, *args, **kwargs):
        if kwargs['user_id']:
            return User.objects.get(pk=kwargs['user_id']['pk']).to_json()
        return jsonify({}), 204


class UserLogin(Resource):

    def __init__(self):
        super(UserLogin, self).__init__()

    def post(self, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            email = data.get('email')
            password = data.get('password')
            pwd = hashlib.sha1(password)
            try:
                user = User.objects.get(email=email,
                                        password=pwd.hexdigest(),
                                        active=True)
                token = generate_token(str(user.pk))
                Token.save_token_for_user(user,
                                          app_token=token,
                                          social_token='',
                                          provider='Custom Login',
                                          expire_in=10000)
                return jsonify({'token': token, 'expire': 10000}), 200
            except DoesNotExist:
                return jsonify({'error': 'Login Incorrect'}), 404
        return jsonify({'error': 'Bad Request'}), 400


class UserRegister(Resource):

    def __init__(self):
        super(UserRegister, self).__init__()


    def post(self, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            email = data.get('email')
            password = data.get('password')
            pwd = hashlib.sha1(password)
            try:
                User.objects.get(email=email)
                return jsonify({'error': 'Email already exists'}), 400
            except DoesNotExist:
                user = User()
                user.email = email
                user.password = pwd.hexdigest()
                user.first_name = data.get('firstname')
                user.last_name = data.get('lastname')
                user.active = False
                token = generate_token(str(user.email))
                user.activation_token = token
                send_activation_email_async(user)
                user.save()

                return jsonify({'success': True}), 200

        return jsonify({'error': 'Bad Request'}), 400


class UserActivate(Resource):

    def __init__(self):
        super(UserActivate, self).__init__()

    def get(self, code, *args, **kwargs):
        try:
            user = User.objects.get(activation_token=code)
            user.active = True
            user.save()
            token = generate_token(str(user.pk))
            Token.save_token_for_user(user,
                                      app_token=token,
                                      social_token='',
                                      provider='Custom Login',
                                      expire_in=10000)
            return jsonify({'token': token, 'expire': 10000}), 200
        except DoesNotExist:
            return jsonify({'error': 'Bad Request'}), 400


class UserNotifications(AuthResource):

    def __init__(self):
        super(UserNotifications, self).__init__()

    def get(self, *args, **kwargs):
        data = UserNotification.objects(user=kwargs['user_id']['pk'])\
                   .order_by('viewed')\
                   .order_by('activity__when')
        if request.args.get('total'):
            data = data[:int(request.args.get('total'))]
        return data.to_json(), 200

    def put(self, *args, **kwargs):
        UserNotification.objects(user=kwargs['user_id']['pk']).update(set__viewed=True)
        data = UserNotification.objects(user=kwargs['user_id']['pk']).order_by('activity__when').to_json()
        if request.args.get('total'):
            data = data[:int(request.args.get('total'))]
        return data, 200