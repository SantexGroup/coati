"""
Notifications module.
"""

from coati.notifications.mail import get_mail_handler


class NotificationCenter(object):
    """
    NotificationCenter class.
    Manages all notification handlers.
    """
    def __init__(self, app=None):
        self.mail_handler = None

        if app is not None:
            self.app = app
            self.init_app(app)

    def init_app(self, app):
        self.mail_handler = get_mail_handler(app)

    def send(self, message):
        """
        Sends a message through the correct plugin.
        :param message: Message to send.
        """
        # TODO implement different plugins handling.
        self.mail_handler.send_async(message)