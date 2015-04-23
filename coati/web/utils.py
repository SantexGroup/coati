import urllib

from flask import current_app, url_for, render_template
from itsdangerous import JSONWebSignatureSerializer

from coati.web.api.auth.utils import current_user

from coati.core.models.notification import store_notification


def serialize_data(data):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(data)


def deserialize_data(data):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.loads(data)


def save_notification(project_pk, verb, data=None, user_to=None):
    store_notification(current_user, project_pk, verb, data, user_to)


def get_template(template_name, **kwargs):
    """
    Gets the correct template for the current locale.
    :param template_name: The template's name.
    :param sub_folder: The subfolder where the template is.
    :return: Rendered template.
    """
    template = render_template(
        '{name}'.format(
            name=template_name
        ),
        **kwargs
    )

    return template


def get_base_url():
    """
    Auxiliary function to get the base url.
    :return: The server's base url.
    """
    return url_for('home', _external=True)


def custom_url_for(path, **params):
    """
    Helper function to generate urls without the need of a flask view.
    :param path: The url path (i.e. `files/file.txt`).
    :param params: The url parameters.
    :return: The absolute url for that path and parameters.
    """
    hostname = get_base_url()
    url_params = '?{}'.format(urllib.urlencode(params))

    absolute_url = hostname + path + url_params

    return absolute_url


