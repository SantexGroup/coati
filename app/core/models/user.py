from app.core import db
from app.core.validators import email_validator
from app.core.models import RootDocument


class User(RootDocument):
    __collection__ = 'users'
    structure = {
        'first_name': unicode,
        'last_name': unicode,
        'active': bool,
        'email': unicode,
        'password': unicode,
        'activation_token': unicode,
        'picture': unicode
    }
    required_fields = ['first_name', 'last_name', 'email']
    default_values = {
        'active': True
    }
    excluded_fields = ['password']
    indexes = [
        {
            'fields': 'email',
            'unique': True,
        },
    ]
    validators = {
        'email': email_validator
    }


db.register(User)