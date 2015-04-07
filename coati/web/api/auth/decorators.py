"""
Auth decorators.
require_authentication
    Checks if a user is authenticated.
require_permissions
    Checks if a user has access to a resource.
"""

from functools import wraps

from flask import g as flask_g

from coati.web.api import errors as api_errors
from coati.web.api.auth.utils import current_user


def has_permissions(user_id):
    """
    Checks whether the current User has permissions or not.
    Admins have access to everything.
    :param user_id: The user's ID on the request.
    :return: Whether the User has permission or not.
    """
    if not current_user:
        return False

    if current_user.is_admin:
        return True

    if user_id:
        # Coati Users have access only to their stuff
        if user_id == 'me' or str(current_user.id) == user_id:
            return True

    return False


def require_permissions(view_func):
    """
    Decorator that verifies if the current user has access over the requested
    resource.
    :param view_func: View to decorate.
    :return: Decorated view.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = kwargs.get('user_id')

        if has_permissions(user_id):
            return view_func(*args, **kwargs)

        raise api_errors.ForbiddenRequest(
            api_errors.UNAUTHORIZED_ACCESS_MSG
        )

    return wrapper


def require_authentication(view_func):
    """
    Decorator that verifies if there is a logged in user.
    :param view_func: View to decorate.
    :return: Decorated view.
    """
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'auth_error' in flask_g:
            raise flask_g.auth_error

        if current_user is None:
            raise api_errors.UnauthorizedRequest(
                api_errors.INVALID_AUTH_TOKEN_MSG
            )

        return view_func(*args, **kwargs)

    return wrapper