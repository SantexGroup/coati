from flask.ext.restful import Api
from resources.sprint import SprintList, SprintInstance, SprintOrder, \
    SprintActive, SprintTickets, SprintChart
from resources.project import ProjectList, ProjectInstance, ProjectColumns, \
    ProjectColumnsOrder, ProjectColumn
from resources.ticket import TicketOrderProject, TicketOrderSprint, TicketProjectList, \
    TicketMovement, TicketInstance, TicketTransition, TicketColumnOrder
from resources.user import UsersList, UserInstance, UserSearch
from app.utils import output_json


def init_app(app, decorators=None):
    api = Api(app,
              default_mediatype='application/json',
              decorators=decorators)

    api.add_resource(ProjectList, '/api/projects')
    api.add_resource(ProjectInstance, '/api/project/<string:project_pk>')
    api.add_resource(ProjectColumns, '/api/project/<string:project_pk>/columns')
    api.add_resource(ProjectColumnsOrder, '/api/project/<string:project_pk>/order_columns')
    api.add_resource(ProjectColumn, '/api/project/column/<string:column_pk>')

    api.add_resource(UsersList, '/api/users')
    api.add_resource(UserSearch, '/api/users/search/<string:query>')
    api.add_resource(UserInstance, '/api/user/<string:pk>')

    api.add_resource(SprintList, '/api/sprints/<string:project_pk>')
    api.add_resource(SprintActive, '/api/sprints/<string:project_pk>/started')
    api.add_resource(SprintOrder, '/api/sprints/<string:project_pk>/order')
    api.add_resource(SprintInstance, '/api/sprint/<string:sp_id>')
    api.add_resource(SprintTickets, '/api/sprint/<string:sprint_id>/tickets')
    api.add_resource(SprintChart, '/api/sprint/<string:sprint_id>/chart')

    api.add_resource(TicketProjectList, '/api/tickets/<string:project_pk>')
    api.add_resource(TicketOrderProject, '/api/tickets/<string:project_pk>/order')
    api.add_resource(TicketOrderSprint, '/api/tickets/sprint/<string:sprint_pk>/order')
    api.add_resource(TicketInstance, '/api/ticket/<string:tkt_id>')

    api.add_resource(TicketMovement, '/api/ticket/movement')
    api.add_resource(TicketTransition, '/api/ticket/transition')
    api.add_resource(TicketColumnOrder, '/api/ticket/column/<string:column>/order')

    api.representations = {'application/json': output_json}