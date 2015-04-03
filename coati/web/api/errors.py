"""
API errors handler.
"""
from coati.core.utils import (
    PASSWORD_ERROR_MSG,
    DUP_NICKNAME_ERROR_MSG,
    DUP_NICKNAME_IN_PAYLOAD_MSG,
    DUP_EMAIL_ERROR_MSG,
    DUP_EMAIL_IN_PAYLOAD_MSG,
    INVALID_EMAIL_MSG,
    SERIAL_ALREADY_ACTIVE_MSG,
)

REQUIRED_MSG = 'Field is required'
REQUIRED_CODE = 1000
DUP_EMAIL_CODE = 1001
DUP_EMAIL_IN_PAYLOAD_CODE = 1002
INVALID_CREDENTIALS_MSG = 'Invalid credentials'
INVALID_CREDENTIALS_CODE = 1003
INVALID_JSON_BODY_MSG = 'Body should be a JSON object'
INVALID_JSON_BODY_CODE = 1004
INVALID_CONTENT_TYPE_MSG = 'Invalid content-type'
INVALID_CONTENT_TYPE_CODE = 1005
MISSING_AUTH_HEADER_MSG = 'Authorization Header missing'
MISSING_AUTH_HEADER_CODE = 1006
INVALID_AUTH_HEADER_MSG = 'Invalid Authorization Header'
INVALID_AUTH_HEADER_CODE = 1007
INVALID_AUTH_TOKEN_MSG = 'Authorization token invalid'
INVALID_AUTH_TOKEN_CODE = 1008
ERROR_PARSING_JSON_MSG = 'Error parsing JSON'
ERROR_PARSING_JSON_CODE = 1009
VALIDATION_ERROR_MSG = 'Validation failed'
VALIDATION_ERROR_CODE = 1010
INVALID_REFRESH_TOKEN_MSG = 'Invalid refresh token'
INVALID_REFRESH_TOKEN_CODE = 1011
INVALID_USER_ID_MSG = 'Invalid User ID'
INVALID_USER_ID_CODE = 1012
PASSWORD_ERROR_CODE = 1013
UNAUTHORIZED_ACCESS_MSG = 'Unauthorized access'
UNAUTHORIZED_ACCESS_CODE = 1014
INVALID_STRING_FIELD_MSG = 'StringField only accepts string values'
INVALID_STRING_FIELD_CODE = 1015
INVALID_STRING_MAX_MSG = 'String value is too long'
INVALID_STRING_MAX_CODE = 1016
INVALID_STRING_MIN_MSG = 'String value is too short'
INVALID_STRING_MIN_CODE = 1017
INVALID_EMAIL_CODE = 1020
SERIAL_ALREADY_ACTIVE_CODE = 1021
PROVIDER_INVALID_MSG = 'Invalid or missing provider'
PROVIDER_INVALID_CODE = 1022
PROVIDER_INVALID_RESP_MSG = 'Invalid response from provider'
PROVIDER_INVALID_RESP_CODE = 1023
PROVIDER_INVALID_TOKEN_MSG = 'Could not validate token from provider'
PROVIDER_INVALID_TOKEN_CODE = 1024
MISSING_AUTH_CODE_MSG = 'Missing authorization code'
MISSING_AUTH_CODE_CODE = 1025
INVALID_USER_MSG = 'Invalid user'
INVALID_USER_CODE = 1026
PSW_RECOVERY_INVALID_TOKEN_MSG = 'Invalid or missing password recovery token'
PSW_RECOVERY_INVALID_TOKEN = 1027
PSW_RECOVERY_EXPIRED_TOKEN_MSG = 'Expired password recovery token'
PSW_RECOVERY_EXPIRED_TOKEN = 1028
PSW_MISSING_PASSWORD_MSG = 'Password or password confirmation missing'
PSW_MISSING_PASSWORD = 1029
PSW_MISSMATCH_PASSWORD_MSG = 'Password and password confirmation do not match'
PSW_MISSMATCH_PASSWORD = 1030
MISSING_PROVIDER_TOKEN_MSG = 'Missing provider\'s token'
MISSING_PROVIDER_TOKEN_CODE = 1031
MISSING_PROVIDER_USER_ID_MSG = 'Missing provider\'s user ID'
MISSING_PROVIDER_USER_ID_CODE = 1032
DUP_NICKNAME_ERROR_CODE = 1034
DUP_NICKNAME_IN_PAYLOAD_CODE = 1035
ACTIVATION_INVALID_TOKEN_MSG = 'Invalid or missing activation token'
ACTIVATION_INVALID_TOKEN = 1036

ERROR_CODES = {
    REQUIRED_MSG: REQUIRED_CODE,
    DUP_EMAIL_ERROR_MSG: DUP_EMAIL_CODE,
    DUP_EMAIL_IN_PAYLOAD_MSG: DUP_EMAIL_IN_PAYLOAD_CODE,
    INVALID_CREDENTIALS_MSG: INVALID_CREDENTIALS_CODE,
    INVALID_JSON_BODY_MSG: INVALID_JSON_BODY_CODE,
    INVALID_CONTENT_TYPE_MSG: INVALID_CONTENT_TYPE_CODE,
    MISSING_AUTH_HEADER_MSG: MISSING_AUTH_HEADER_CODE,
    INVALID_AUTH_HEADER_MSG: INVALID_AUTH_HEADER_CODE,
    INVALID_AUTH_TOKEN_MSG: INVALID_AUTH_TOKEN_CODE,
    ERROR_PARSING_JSON_MSG: ERROR_PARSING_JSON_CODE,
    VALIDATION_ERROR_MSG: VALIDATION_ERROR_CODE,
    INVALID_REFRESH_TOKEN_MSG: INVALID_REFRESH_TOKEN_CODE,
    INVALID_USER_ID_MSG: INVALID_USER_ID_CODE,
    PASSWORD_ERROR_MSG: PASSWORD_ERROR_CODE,
    UNAUTHORIZED_ACCESS_MSG: UNAUTHORIZED_ACCESS_CODE,
    INVALID_STRING_FIELD_MSG: INVALID_STRING_FIELD_CODE,
    INVALID_STRING_MAX_MSG: INVALID_STRING_MAX_CODE,
    INVALID_STRING_MIN_MSG: INVALID_STRING_MIN_CODE,
    INVALID_EMAIL_MSG: INVALID_EMAIL_CODE,
    SERIAL_ALREADY_ACTIVE_MSG: SERIAL_ALREADY_ACTIVE_CODE,
    PROVIDER_INVALID_MSG: PROVIDER_INVALID_CODE,
    PROVIDER_INVALID_RESP_MSG: PROVIDER_INVALID_RESP_CODE,
    PROVIDER_INVALID_TOKEN_MSG: PROVIDER_INVALID_TOKEN_CODE,
    MISSING_PROVIDER_TOKEN_MSG: MISSING_PROVIDER_TOKEN_CODE,
    MISSING_PROVIDER_USER_ID_MSG: MISSING_PROVIDER_USER_ID_CODE,
    DUP_NICKNAME_ERROR_MSG: DUP_NICKNAME_ERROR_CODE,
    DUP_NICKNAME_IN_PAYLOAD_MSG: DUP_NICKNAME_IN_PAYLOAD_CODE,
    MISSING_AUTH_CODE_MSG: MISSING_AUTH_CODE_CODE,
    INVALID_USER_MSG: INVALID_USER_CODE,
    PSW_RECOVERY_INVALID_TOKEN_MSG: PSW_RECOVERY_INVALID_TOKEN,
    PSW_RECOVERY_EXPIRED_TOKEN_MSG: PSW_RECOVERY_EXPIRED_TOKEN,
    PSW_MISSING_PASSWORD_MSG: PSW_MISSING_PASSWORD,
    PSW_MISSMATCH_PASSWORD_MSG: PSW_MISSMATCH_PASSWORD,
    ACTIVATION_INVALID_TOKEN_MSG: ACTIVATION_INVALID_TOKEN
}


class BasicAPIException(Exception):
    """
    Basic api exception.
    """
    code = 500

    def get_code(self):
        return get_code(self.message)

    @property
    def data(self):
        """
        Data property used to return a JSON body with `message` and `code`.
        """
        return dict(
            message=self.message,
            code=self.get_code()
        )


class InvalidAPIUsage(BasicAPIException):
    """
    Exception for 400 HTTP errors in the API.
    """
    code = 400

    def __init__(self, *args, **kwargs):
        self.payload = kwargs.get('payload')
        super(InvalidAPIUsage, self).__init__(*args)

    @property
    def data(self):
        """
        Adds an `error` key to the response JSON with the error code for the
        specific field errors.
        """
        _data = dict(message=self.message, code=self.get_code())

        if self.payload:
            err_list = []
            for err_json in self.payload:
                err_dict = {}
                for field, message in err_json.iteritems():
                    err_dict = add_code(err_dict, field, message)
                err_list.append(err_dict)

            _data['errors'] = err_list

        return _data


class UnauthorizedRequest(BasicAPIException):
    """
    Exception for 401 HTTP errors in the API.
    """
    code = 401


class ForbiddenRequest(BasicAPIException):
    """
    Exception for 403 HTTP errors in the API.
    """
    code = 403


class NotAcceptable(BasicAPIException):
    """
    Exception for a 406 HTTP error.
    """
    code = 406
    message = 'Accepted MIME types: {!r}'

    def __init__(self, *args, **kwargs):
        accepted_types = kwargs.get('accepted')
        self.message = self.message.format(accepted_types)

        super(NotAcceptable, self).__init__(*args)

    def get_code(self):
        return self.code


class MissingResource(BasicAPIException):
    """
    Exception for 404 HTTP errors in the API.
    """
    code = 404


def get_code(message):
    """
    Auxiliary function to get the internal error codes.
    :param message:
    :return:
    """
    return ERROR_CODES.get(message)


def add_code(err_dict, field, message):
    """
    Auxiliary function to format payloads with internal codes.
    """
    if field != '_object':
        err_dict.update(
            {
                field: [{'message': message, 'code': get_code(message)}]
            }
        )
    else:
        err_dict.update({field: message})

    return err_dict