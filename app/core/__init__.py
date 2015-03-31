from flask.ext.mongokit import MongoKit

db = MongoKit()


def init_app(app):
    db.init_app(app)
