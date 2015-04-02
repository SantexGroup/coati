from flask.ext.restful import Resource
from coati.web.auth.decorators import require_authentication

__author__ = 'gastonrobledo'


class AuthResource(Resource):

    decorators = [require_authentication]