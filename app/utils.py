import os
import threading
from flask import make_response, current_app, copy_current_request_context
from flask_mail import Mail, Message
from itsdangerous import JSONWebSignatureSerializer
from jinja2 import Environment, FileSystemLoader
from app.schemas import UserActivity, Project, User


def serialize_data(data):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(data)


def deserialize_data(data):
    s = JSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.loads(data)


def send_activation_email_async(*args):
    send_email_async(create_activation_email, *args)


def send_new_member_email_async(*args):
    send_email_async(create_new_member_email, *args)


def create_activation_email(user):
    path = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(path + '/templates'))
    template = env.get_template('activation_email.html')
    link = '%s/login/activate_user/%s' % (current_app.config['CURRENT_DOMAIN'],
                                          user.activation_token)
    msg = Message(subject='Coati - Activation Email',
                  recipients=[user.email],
                  html=template.render(link=link))
    return msg


def create_new_member_email(user, project):
    path = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(path + '/templates'))
    template = env.get_template('new_member.html')
    link = '%s/project/%s' % (current_app.config['CURRENT_DOMAIN'],
                              str(project.pk))
    msg = Message(subject='Coati - Project Participation',
                  recipients=[user.email],
                  html=template.render(link=link, name=project.name))
    return msg


def send_email_async(function, *args):
    mail = Mail(app=current_app)
    msg = function(*args)

    @copy_current_request_context
    def send_message(message):
        mail.send(message)

    sender = threading.Thread(name='mail_sender', target=send_message,
                              args=(msg,))
    sender.start()


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


def save_notification(project_pk, author, verb, data=None, user_to=None):
    ua = UserActivity()
    ua.project = Project.objects.get(pk=project_pk)
    ua.author = User.objects.get(pk=author)
    ua.verb = verb
    ua.data = data
    ua.to = user_to
    ua.save()










