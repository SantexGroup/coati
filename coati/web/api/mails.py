from flask import current_app
from flask.ext.mail import Message
from coati.web.utils import custom_url_for, get_template


def create_activation_email(user):
    link = custom_url_for(
        '/login/activate_user',
        token=user.activation_token
    )
    message = Message(
        'Coati - Activation Email',
        sender=(
            current_app.config.get('MAIL_SENDER_NAME'),
            current_app.config.get('MAIL_DEFAULT_SENDER')
        ),
        recipients=[user.email]
    )

    message.html = get_template(
        'activation_email.html',
        full_name=user.full_name,
        link=link
    )

    current_app.notification_handler.send(message)


def create_new_member_email(user, project):
    link = custom_url_for(
        '/project/%s',
        token=str(project.pk)
    )
    message = Message(
        'Coati - Project Participation',
        sender=(
            current_app.config.get('MAIL_SENDER_NAME'),
            current_app.config.get('MAIL_DEFAULT_SENDER')
        ),
        recipients=[user.email]
    )

    message.html = get_template(
        'new_member.html',
        full_name=user.full_name,
        link=link,
        name=project.name
    )
    current_app.notification_handler.send(message)


def create_notification_email(user, comment):
    link = custom_url_for(
        '/project/%s/planning/ticket/%s',
        project=str(comment.ticket.project.pk),
        ticket=str(comment.ticket.pk)
    )
    message = Message(
        'Coati - Notification',
        sender=(
            current_app.config.get('MAIL_SENDER_NAME'),
            current_app.config.get('MAIL_DEFAULT_SENDER')
        ),
        recipients=[user.email]
    )

    message.html = get_template(
        'notification.html',
        full_name=user.full_name,
        link=link,
        message=comment.comment,
        title=comment.ticket.title
    )
    current_app.notification_handler.send(message)
