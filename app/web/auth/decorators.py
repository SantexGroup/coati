import json
from functools import wraps

from flask import request, g
from app.auth.tools import get_data_from_token, verify_token, \
    check_user_permissions

from app.utils import output_json

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
        token_data = verify_token(token)
        if token_data is not None:
            g.user_id = token_data['pk']
            if check_user_permissions(g.user_id, kwargs.get('project_pk')):
                return view_function(*args, **kwargs)
            else:
                res = output_json(
                    json.dumps({'error': 'You do not have permissions.'}),
                    code=403)
                res.content_type = 'application/json'
                return res
        else:
            res = output_json(
                json.dumps({'error': 'Authorization token invalid'}),
                code=401)
            res.content_type = 'application/json'
            return res

    return decorated_function