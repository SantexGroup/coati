"""
Mailing module.
"""

import threading

from flask import copy_current_request_context
from flask.ext.mail import Mail


class MailPlugin(Mail):
    """
    MailPlugin class, extends from Flask-Mail's Mail class.
    """

    def send_async(self, msg):
        """
        Sends an email asynchronously.
        :param msg: The message to send.
        """
        @copy_current_request_context
        def send_message(message):
            self.send(message)

        sender = threading.Thread(
            name='mail_sender',
            target=send_message,
            args=(msg, )
        )
        sender.start()


def get_mail_handler(app):
    """
    Mail handler getter.
    :param app: A Flask app
    :return: A Flask-Mail's Mail object
    """
    return MailPlugin(app)