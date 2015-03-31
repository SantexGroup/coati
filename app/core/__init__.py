from app.core.flask_mongokit import MongoKit

db = MongoKit()


def init_app(app):
    db.init_app(app)
