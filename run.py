"""
Script to initialize Flask App.
"""

from flask.ext.script import Manager  # pylint: disable=import-error

from app.web import create_app

import config

app = create_app(config)


if not app.debug:
    # Configure the app's logger only when not in debug
    import logging
    from logging import handlers

    # Use a rotating file handler with a maximum of 10 files of 10MB each
    file_handler = handlers.RotatingFileHandler(
        'gibike_flask.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )

    # Format: <DATE> <TIME> <LOG_LEVEL>: <MESSAGE> [in <FILE_PATH>:<LINE_NO>]
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
    )
    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)

    # Configure error logging by email
    mail_handler = handlers.SMTPHandler(
        app.config.get('EMAIL_HOST'),
        app.config.get('EMAIL_FROM'),
        app.config.get('ADMIN_EMAILS'),
        '[Gibike] An error occurred'
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


if __name__ == '__main__':
    manager = Manager(app)
    manager.run()