from flask.ext.restful import Api
from resources.sprint import SprintList, SprintInstance
from resources.project import ProjectList, ProjectInstance
from resources.ticket import TicketList
from resources.user import UsersList, UserInstance
from app.utils import output_json


def init_app(app):
    api = Api(app, default_mediatype='application/json')
    api.add_resource(ProjectList, '/api/projects')
    api.add_resource(ProjectInstance, '/api/project/<string:slug>')
    api.add_resource(UsersList, '/api/users')
    api.add_resource(UserInstance, '/api/user/<string:pk>')
    api.add_resource(TicketList, '/api/tickets/<string:project_pk>')
    api.add_resource(SprintList, '/api/sprints/<string:project_pk>')
    api.add_resource(SprintInstance, '/api/sprint/<string:sp_id>')
    api.representations = {'application/json': output_json}
