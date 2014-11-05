import functools
import json
from flask import make_response, request
from mongoengine import DoesNotExist
from app.schemas import Token

__author__ = 'gastonrobledo'

def output_json(obj, code, headers=None):
    """
    This is needed because we need to use a custom JSON converter
    that knows how to translate MongoDB types to JSON.
    """
    resp = make_response(obj, code)
    resp.headers.extend(headers or {})

    return resp


def verify_token(token):
    try:
        return Token.objects.get(token=token) is not None
    except DoesNotExist:
        return False


def require_authentication(view_function):
    @functools.wraps(view_function)
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
        if verify_token(token):
            return view_function(*args, **kwargs)
        else:
            res = output_json(json.dumps({'error': 'Authorization token invalid'}),
                              code=401)
            res.content_type = 'application/json'
            return res

    return decorated_function