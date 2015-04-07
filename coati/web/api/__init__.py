"""
API main module.
"""
import simplejson

from bson import json_util
from itsdangerous import TimedJSONWebSignatureSerializer

from flask import blueprints, make_response, current_app, request
from flask.ext import restful

from coati.notifications import NotificationCenter
from coati.web.api import project, sprint, ticket, user, errors
from coati.web.api import auth, tokens


APP_ACCEPTED_TYPE = 'application/json'

blueprint = blueprints.Blueprint(
    'coati.web.api',
    __name__,
    url_prefix='/api/v1'
)

api = restful.Api(blueprint, default_mediatype='application/json')

api.add_resource(auth.Authorized, '/auth/authorized')
api.add_resource(tokens.AccessToken, '/token')
api.add_resource(tokens.RefreshToken, '/refresh_token')

api.add_resource(user.UsersList, '/users')
api.add_resource(user.UserInstance, '/users/<string:user_id>')
api.add_resource(user.UserNotifications,
                 '/users/<string:user_id>/notifications')
api.add_resource(user.UserSearch, '/users/search/<string:query>')
api.add_resource(user.UserActivate, '/users/activate/<string:code>')

api.add_resource(project.ProjectList,
                 '/projects/<string:user_id>')
api.add_resource(project.ProjectInstance,
                 '/projects/<string:project_pk>')
api.add_resource(project.ProjectColumns,
                 '/projects/<string:project_pk>/columns')
api.add_resource(project.ProjectColumnsOrder,
                 '/projects/<string:project_pk>/order_columns')
api.add_resource(project.ProjectMembers,
                 '/projects/<string:project_pk>/members')
api.add_resource(project.ProjectMemberInstance,
                 '/projects/<string:project_pk>/members/<string:member_pk>')
api.add_resource(project.ProjectImport,
                 '/projects/<string:project_pk>/import')
api.add_resource(project.ProjectColumn,
                 '/projects/<string:project_pk>/column/<string:column_pk>')

api.add_resource(sprint.SprintList, '/projects/<string:project_pk>/sprints')
api.add_resource(sprint.SprintArchivedList,
                 '/projects/<string:project_pk>/sprints/archived')
api.add_resource(sprint.SprintAllList,
                 '/projects/<string:project_pk>/sprints/all')
api.add_resource(sprint.SprintActive,
                 '/projects/<string:project_pk>/sprints/started')
api.add_resource(sprint.SprintOrder,
                 '/projects/<string:project_pk>/sprints/order')
api.add_resource(sprint.SprintInstance,
                 '/projects/<string:project_pk>/sprint/<string:sp_id>')
api.add_resource(sprint.SprintTickets,
                 '/projects/<string:project_pk>/sprint/<string:sprint_id>/tickets')
api.add_resource(sprint.SprintChart,
                 '/projects/<string:project_pk>/sprint/<string:sprint_id>/chart')

api.add_resource(ticket.TicketProjectList,
                 '/projects/<string:project_pk>/tickets')

api.add_resource(ticket.TicketBoardProject,
                 '/projects/<string:project_pk>/tickets/board')
api.add_resource(ticket.TicketOrderProject,
                 '/projects/<string:project_pk>/tickets/order')
api.add_resource(ticket.TicketOrderSprint,
                 '/projects/<string:project_pk>/tickets/sprint/<string:sprint_pk>/order')
api.add_resource(ticket.TicketSearch, '/projects/tickets/search/<string:query>')
api.add_resource(ticket.TicketSearchRelated,
                 '/projects/<string:project_pk>/tickets/search/<string:query>')

api.add_resource(ticket.TicketClosed,
                 '/projects/<string:project_pk>/tickets/archived')
api.add_resource(ticket.TicketInstance,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>')
api.add_resource(ticket.TicketRelated,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>/related/<string:rtkt_id>')
api.add_resource(ticket.TicketClone,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>/clone')
api.add_resource(ticket.TicketComments,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>/comments')
api.add_resource(ticket.CommentInstance,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>/comment/<string:comment_id>')
api.add_resource(ticket.TicketAttachments,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>/attachments')
api.add_resource(ticket.AttachmentInstance,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>/attachments/<string:att_id>/delete')
api.add_resource(ticket.MemberTicketInstance,
                 '/projects/<string:project_pk>/ticket/<string:tkt_id>/assignments/<string:member_id>')
api.add_resource(ticket.TicketMovement,
                 '/projects/<string:project_pk>/ticket/movement')
api.add_resource(ticket.TicketTransition,
                 '/projects/<string:project_pk>/ticket/transition')
api.add_resource(ticket.TicketColumnOrder,
                 '/projects/<string:project_pk>/ticket/column/<string:column>/order')

# Get the current logged in user (if any)
blueprint.before_request(auth.get_user_from_token)


@blueprint.before_request
def detect_mime_type():
    """
    Check all API requests for `application/json` media type.
    :raise: InvalidAPIUsage error if an incorrect type was used.
    """
    headers_dict = dict(request.headers)

    if request.method in ['POST', 'PUT']:
        # For POST/PUT we need to check the content type
        content_type = headers_dict.get('Content-Type')

        if APP_ACCEPTED_TYPE not in content_type:
            raise errors.InvalidAPIUsage(errors.INVALID_CONTENT_TYPE_MSG)
    else:
        # For GET/DELETE we need to check the accept types
        accept_types = headers_dict.get('Accept')

        # If there are no accepted types, we assume the client accepts ours
        if accept_types:
            accepts_our_mime = (
                (APP_ACCEPTED_TYPE in accept_types) or
                ('*/*' in accept_types)
            )

            if not accepts_our_mime:
                raise errors.NotAcceptable(accepted=APP_ACCEPTED_TYPE)


@blueprint.after_request
def remove_auth_challenge(response):
    """
    Fix for removing the authenticate challenge added by flask-restful when
    a 401 code is returned.
    :param response: A response object.
    :return: The response object without the `WWW-Authenticate` header.
    """
    response.headers.pop('WWW-Authenticate', None)

    return response


@api.representation('application/json')
def output_json(data, code, headers=None):
    """
    Additional representation transformer.
    Uses simple_json instead of json to make the response. Adds indentation
    if the app is in DEBUG mode.
    :param data: The data to be represented in the response body
    :param code: The http status code
    :param headers: A dictionary of headers
    :return: A flask response object.
    """
    indent = None

    if current_app.config.get('DEBUG'):
        indent = current_app.config.get('JSON_INDENT', 2)

    response = make_response(
        simplejson.dumps(data, indent=indent, default=json_util.default),
        code
    )

    response.headers.extend(headers or {})

    return response


def init_app(app):
    """
    Register `coati.api` blueprint.
    :param app: Flask application.
    """
    auth.init_app(app)
    app.notification_handler = NotificationCenter(app)

    app.token_handler = auth.utils.TokenHandler(
        secret=app.config.get('SECRET_KEY'),
        expires_in=app.config.get('TOKEN_EXPIRATION_TIME')
    )
    app.recovery_token_handler = TimedJSONWebSignatureSerializer(
        app.config.get('SECRET_KEY'),
        expires_in=app.config.get('MAIL_RECOVERY_TIME')
    )

    app.register_blueprint(blueprint)