from flask.ext.restful import Api
from resources.sprint import SprintList, SprintInstance, SprintOrder, \
    SprintActive, SprintTickets, SprintChart, SprintArchivedList, SprintAllList
from resources.project import ProjectList, ProjectInstance, ProjectColumns, \
    ProjectColumnsOrder, ProjectColumn, ProjectMembers, ProjectImport
from resources.ticket import TicketOrderProject, TicketOrderSprint, TicketProjectList, \
    TicketMovement, TicketInstance, TicketTransition, TicketColumnOrder, \
    TicketComments, TicketAttachments, AttachmentInstance, MemberTicketInstance, \
    TicketSearch, TicketClosed
from resources.user import UsersList, UserInstance, UserSearch, UserLogged, \
    UserLogin, UserRegister, UserActivate, UserNotifications
from app.utils import output_json


def init_app(app, decorators=None):
    api = Api(app,
              default_mediatype='application/json',
              decorators=decorators,
              prefix='/api')

    api.add_resource(ProjectList, '/projects')
    api.add_resource(ProjectInstance, '/project/<string:project_pk>')
    api.add_resource(ProjectColumns, '/project/<string:project_pk>/columns')
    api.add_resource(ProjectColumnsOrder, '/project/<string:project_pk>/order_columns')
    api.add_resource(ProjectMembers, '/project/<string:project_pk>/members')
    api.add_resource(ProjectImport, '/project/<string:project_pk>/import')
    api.add_resource(ProjectColumn, '/project/<string:project_pk>/column/<string:column_pk>')

    api.add_resource(UsersList, '/users')
    api.add_resource(UserSearch, '/users/search/<string:query>')
    api.add_resource(UserInstance, '/user/<string:pk>')
    api.add_resource(UserLogged, '/user/me')
    api.add_resource(UserLogin, '/user/login')
    api.add_resource(UserRegister, '/user/register')
    api.add_resource(UserActivate, '/user/activate/<string:code>')
    api.add_resource(UserNotifications, '/user/notifications')

    api.add_resource(SprintList, '/project/<string:project_pk>/sprints')
    api.add_resource(SprintArchivedList, '/project/<string:project_pk>/sprints/archived')
    api.add_resource(SprintAllList, '/project/<string:project_pk>/sprints/all')
    api.add_resource(SprintActive, '/project/<string:project_pk>/sprints/started')
    api.add_resource(SprintOrder, '/project/<string:project_pk>/sprints/order')
    api.add_resource(SprintInstance, '/project/<string:project_pk>/sprint/<string:sp_id>')
    api.add_resource(SprintTickets, '/project/<string:project_pk>/sprint/<string:sprint_id>/tickets')
    api.add_resource(SprintChart, '/project/<string:project_pk>/sprint/<string:sprint_id>/chart')

    api.add_resource(TicketProjectList, '/project/<string:project_pk>/tickets')
    api.add_resource(TicketOrderProject, '/project/<string:project_pk>/tickets/order')
    api.add_resource(TicketOrderSprint, '/project/<string:project_pk>/tickets/sprint/<string:sprint_pk>/order')
    api.add_resource(TicketSearch, '/tickets/search/<string:query>')
    api.add_resource(TicketClosed, '/project/<string:project_pk>/tickets/archived')
    api.add_resource(TicketInstance, '/project/<string:project_pk>/ticket/<string:tkt_id>')
    api.add_resource(TicketComments, '/project/<string:project_pk>/ticket/<string:tkt_id>/comments')
    api.add_resource(TicketAttachments, '/project/<string:project_pk>/ticket/<string:tkt_id>/attachments')
    api.add_resource(AttachmentInstance, '/project/<string:project_pk>/ticket/<string:tkt_id>/attachments/<string:att_id>/delete')
    api.add_resource(MemberTicketInstance, '/project/<string:project_pk>/ticket/<string:tkt_id>/assignments/<string:member_id>')
    api.add_resource(TicketMovement, '/project/<string:project_pk>/ticket/movement')
    api.add_resource(TicketTransition, '/project/<string:project_pk>/ticket/transition')
    api.add_resource(TicketColumnOrder, '/project/<string:project_pk>/ticket/column/<string:column>/order')

    api.representations = {'application/json': output_json}