from mongoengine import Q, errors as mongo_errors
from werkzeug.security import generate_password_hash, check_password_hash
from coati.core import db, utils


class User(db.Document):
    email = db.StringField(required=True)
    password = db.StringField(required=False)
    first_name = db.StringField(max_length=50)
    last_name = db.StringField(max_length=50)
    activation_token = db.StringField()
    active = db.BooleanField(default=True)
    picture = db.StringField()

    meta = {
        'indexes': [{'fields': ['email'], 'sparse': True, 'unique': True}]
    }

    excluded_fields = ['activation_token', 'password']

    def set_password(self, password):
        utils.validate_password(password)
        self.password = generate_password_hash(password, 'sha1')

    def verify_password(self, pwd):
        return pwd is not None and check_password_hash(
            self.password,
            pwd
        )

    def validate(self, clean=True):
        err_dict = {}

        try:
            if self.password:
                utils.validate_password(self.password)
        except mongo_errors.ValidationError as ex:
            err_dict.update(ex.to_dict())

        try:
            super(User, self).validate(clean=clean)
        except mongo_errors.ValidationError as ex:
            err_dict.update(ex.to_dict())

        if err_dict:
            raise mongo_errors.ValidationError(errors=err_dict)

    @classmethod
    def validate_duplicated_email(cls, email):
        """
        Validates if the email is already in use.
        :param email: The email to validate.
        :return: Dict with {field: error}.
        """

        if cls.objects(email=email):
            return dict(email=utils.DUP_EMAIL_ERROR_MSG)

    @classmethod
    def get_by_email(cls, email):
        """
        Returns User by email if it exists.
        :param email: The email to filter by.
        :return: A user instance or None if the email is not in use.
        """
        try:
            instance = cls.objects.filter(active=True, email=email).first()
        except (mongo_errors.ValidationError, cls.DoesNotExist):
            instance = None

        return instance

    @classmethod
    def get_by_activation_token(cls, token_activation):
        """
        Returns User by activation token if it exists.
        :param token_activation: The email to filter by.
        :return: A user instance or None if the token_activation is not in use.
        """
        try:
            instance = cls.objects.filter(active=False,
                                          activation_token=token_activation).first()
        except (mongo_errors.ValidationError, cls.DoesNotExist):
            instance = None

        return instance

    @classmethod
    def get_or_create(cls, **kwargs):
        """
        Gets or creates a User, using the provided data.
        An email must always be provided.
        :param kwargs: keyword arguments to be passed to the model constructor.
        :return: A tuple with the user instance and a boolean indicating
            whether the user was created or not.
        """
        created = False

        email = kwargs.get('email')
        if not email:
            raise ValueError('No email provided')

        instance = cls.get_by_email(email=email)

        if not instance:
            created = True
            instance = cls(**kwargs)

        return instance, created

    def save(self, force_insert=False, **kwargs):
        doc = self.to_mongo()

        created = ('_id' not in doc or self._created or force_insert)

        if created:
            # Set a password on creation (even if one wasn't provided)
            password = self.password or utils.generate_random_password()
            self.set_password(password)

        return super(User, self).save(force_insert=force_insert, **kwargs)

    @classmethod
    def search(cls, query):
        return cls.objects(Q(email__istartswith=query) |
                           Q(first_name__istartswith=query) |
                           Q(last_name__istartswith=query))