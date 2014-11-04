__author__ = 'gastonrobledo'

from flask.ext.restful import Resource
from app.schemas import User


class UsersList(Resource):

    def __init__(self):
        super(UsersList, self).__init__()


    def get(self):
        return User.objects.all().to_json()


class UserInstance(Resource):

    def __init__(self):
        super(UserInstance, self).__init__()

    def get(self, pk):
        return User.objects.get(id=pk).to_json()

    def put(self, pk):
        pass

    def delete(self, pk):
        pass