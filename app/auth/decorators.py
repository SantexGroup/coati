import json
from functools import wraps

from flask import request
from app.auth.tools import get_data_from_token

from app.utils import output_json
from app.schemas import Token

__author__ = 'gastonrobledo'


def require_authentication(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        header = request.headers.environ.get('HTTP_AUTHORIZATION')
        if not header:
            res = output_json(json.dumps(
                {'error': 'Authorization header missing.'}
            ), code=401)
            res.content_type = 'application/json'
            return res
        token = header.split(' ')[1]
        if Token.verify_token(token):
            kwargs['user_id'] = get_data_from_token(token)
            return view_function(*args, **kwargs)
        else:
            res = output_json(
                json.dumps({'error': 'Authorization token invalid'}),
                code=401)
            res.content_type = 'application/json'
            return res

    return decorated_function