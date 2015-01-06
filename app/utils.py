import os
from flask import make_response, current_app
from flask_mail import Mail, Message
from itsdangerous import JSONWebSignatureSerializer
from jinja2 import Environment, FileSystemLoader



__author__ = 'gastonrobledo'


def serialize_data(data):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(data)


def deserialize_data(data):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.loads(data)


def send_activation_email(user):
    mail = Mail(app=current_app)
    path = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(path + '/templates'))
    template = env.get_template('activation_email.html')
    link = '%s/login/activate_user/%s' % (current_app.config['CURRENT_DOMAIN'],
                                          user.activation_token)
    msg = Message(subject='Coati - Activation Email',
                  recipients=[user.email],
                  html=template.render(link=link))
    mail.send(msg)


def send_new_member_email(user, project):
    mail = Mail(app=current_app)
    path = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(path + '/templates'))
    template = env.get_template('new_member.html')
    link = '%s/project/%s' % (current_app.config['CURRENT_DOMAIN'],
                              str(project.pk))
    msg = Message(subject='Coati - Project Participation',
                  recipients=[user.email],
                  html=template.render(link=link, name=project.name))
    mail.send(msg)



def output_json(obj, code, headers=None):
    """
    This is needed because we need to use a custom JSON converter
    that knows how to translate MongoDB types to JSON.
    """

    try:
        resp = make_response(obj, code)
        resp.headers.extend(headers or {})
    except Exception as ex:
        # logged into the log.txt file
        pass

    return resp










