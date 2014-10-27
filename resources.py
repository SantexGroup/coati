from flask.ext.restful import Resource, request
from schemas import User, Column, Project


class ProjectList(Resource):

    def __init__(self):
        super(ProjectList, self).__init__()


    def get(self):
        return Project.objects.all().to_json()

    def post(self):
        data = request.json
        prj = Project(name=data.get('name'),
                      owner=User.objects.get(id=data.get('owner')).to_dbref())
        prj.active = data.get('active')
        prj.private = data.get('private')
        prj.description = data.get('description')

        for col in data.get('columns'):
            column = Column()
            column.title = col.get('title')
            column.max_cards = col.get('max_cards')
            prj.columns.append(column)
        prj.save()
        return prj.to_json(), 201


class ProjectInstance(Resource):

    def get(self, project_id):
        return Project.objects(id=project_id).to_json()

    def put(self, project_id):
        pass

    def delete(self, project_id):
        pass


class UsersList(Resource):

    def __init__(self):
        super(UsersList, self).__init__()


    def get(self):
        return User.objects.all().to_json()

    def post(self):
        data = request.json
        usr = User()
        usr.email = data.get('email')
        usr.first_name = data.get('first_name')
        usr.last_name = data.get('last_name')
        usr.save()
        return usr.to_json(), 201