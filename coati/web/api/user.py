from mongoengine import errors as mongo_errors
from flask import request
from flask.ext.restful import Resource
from coati.core.models.user import User

from coati.web.api.auth import AuthResource, current_user
from coati.web.api import errors as api_errors


def get_user_for_request(user_id):
    """
    Get a user by ID
    :param user_id: Id of the User
    :return: User Instance
    """
    if user_id == 'me':
        # TODO: Find a better way to do this
        # Workaround: mongoengine can not always deal with proxies'
        return current_user._get_current_object()

    return User.get_by_id(user_id)


def create_user(user_data):
    """
    Creates a User instance with the given user data.
    If errors occur during validation, also returns an error JSON.
    :param user_data: The user's data.
    :return: Tuple in the form (user, errors).
    """
    errors_dic = {}

    user = User(
        first_name=user_data.get('first_name'),
        last_name=user_data.get('last_name'),
        email=user_data.get('email'),
        password=user_data.get('password')
    )

    try:
        user.validate()
    except mongo_errors.ValidationError as ex:
        errors_dic = ex.to_dict()

        errors_dic.update(
            _object=user_data
        )

    dup_errors = [User.validate_duplicated_email(user.email)]

    for dup_error in dup_errors:
        if dup_error:
            errors_dic.update(dup_error, _object=user_data)

    return user, errors_dic


class UsersList(AuthResource):
    """
    User Resource
    """

    def get(self):
        """
        Returns the list of users
        :return: A List of json representing users.
        """
        return User.objects.all().to_json()

    def post(self):
        """
        Create user resource
        :return: a Created resource
        """
        user_data = request.get_json(silent=True)
        if not user_data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        user, errors_dic = create_user(user_data)
        errors_list = []
        if errors_dic:
            errors_list.append(errors_dic)

        if errors_list:
            raise api_errors.InvalidAPIUsage(
                api_errors.VALIDATION_ERROR_MSG,
                payload=errors_list
            )

        return user.to_dict(), 201


class UserSearch(AuthResource):
    """
    Search users
    """

    def get(self, query):
        """
        Return the list of users matching the query string.
        :param query: the query string to search for a user
        :return: List of json dict text, value
        """
        users = User.search(query=query)
        data = []
        for u in users:
            val = dict(text=u.email, value=str(u.pk))
            data.append(val)
        return data


class UserInstance(AuthResource):
    """
    User Resource
    """

    def get(self, user_id):
        """
        Get an instance of a user.
        :param user_id: ID of the user
        :return: a User Object
        """
        user = get_user_for_request(user_id)
        if not user:
            raise api_errors.MissingResource(
                api_errors.INVALID_USER_ID_MSG
            )

        return user.to_dict()

    def put(self, user_id):
        """
        Update Resource
        :param user_id: The User ID
        :return: Return a user instance updated
        """
        data = request.get_json(silent=True)
        if data:
            user = get_user_for_request(user_id)
            if not user:
                raise api_errors.MissingResource(
                    api_errors.INVALID_USER_ID_MSG
                )

            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.picture = data.get('picture', user.picture)
            user.email = data.get('email', user.email)

            user.save()

            return user.to_dict(), 200
        raise api_errors.InvalidAPIUsage(api_errors.ERROR_PARSING_JSON_MSG)


    def delete(self, user_id):
        """
        Delete the user
        :param user_id: Id of the User
        :return: No Content
        """
        user = get_user_for_request(user_id)
        if not user:
            raise api_errors.MissingResource(
                api_errors.INVALID_USER_ID_MSG
            )
        user.delete()
        return {}, 204


class UserLogin(Resource):
    """
    Login User
    """
    def post(self):
        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.ERROR_PARSING_JSON_MSG
            )
        email = data.get('email')
        password = data.get('password')
        pwd = hashlib.sha1(password)
        try:
            user = User.objects.get(email=email,
                                    password=pwd.hexdigest(),
                                    active=True)
            token = generate_token(str(user.pk))
            expire = current_app.config['TOKEN_EXPIRATION_TIME']
            return jsonify({'token': token, 'expire': expire}), 200
        except DoesNotExist:
            return jsonify({'error': 'Login Incorrect'}), 404




class UserActivate(Resource):
    def __init__(self):
        super(UserActivate, self).__init__()

    def get(self, code):
        try:
            user = User.objects.get(activation_token=code)
            user.active = True
            user.save()
            token = generate_token(str(user.pk))
            return jsonify({'token': token,
                            'expire': current_app.config[
                                'TOKEN_EXPIRATION_TIME']}), 200
        except DoesNotExist:
            return jsonify({'error': 'Bad Request'}), 400


class UserNotifications(Resource):
    def __init__(self):
        super(UserNotifications, self).__init__()

    def get(self):
        return get_notifications()

    def put(self):
        UserNotification.objects(user=g.user_id).update(set__viewed=True)
        return get_notifications()


def get_notifications():
    notifications = UserNotification.objects(user=g.user_id)
    results = []
    for n in notifications:
        if str(n.activity.author.pk) != g.user_id:
            results.append(json.loads(n.to_json()))

    results.sort(key=lambda x: x['activity']['when']['$date'], reverse=True)
    if request.args.get('total'):
        results = results[:int(request.args.get('total'))]
    return jsonify({'notifications': results}), 200