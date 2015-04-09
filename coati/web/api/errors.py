"""
API errors handler.
"""

REQUIRED_MSG = 'Field is required'
REQUIRED_CODE = 1000
INVALID_CREDENTIALS_MSG = 'Invalid credentials'
INVALID_CREDENTIALS_CODE = 1001
INVALID_JSON_BODY_MSG = 'Body should be a JSON object'
INVALID_JSON_BODY_CODE = 1002
INVALID_CONTENT_TYPE_MSG = 'Invalid content-type'
INVALID_CONTENT_TYPE_CODE = 1003
MISSING_AUTH_HEADER_MSG = 'Authorization Header missing'
MISSING_AUTH_HEADER_CODE = 1004
INVALID_AUTH_HEADER_MSG = 'Invalid Authorization Header'
INVALID_AUTH_HEADER_CODE = 1005
INVALID_AUTH_TOKEN_MSG = 'Authorization token invalid'
INVALID_AUTH_TOKEN_CODE = 1006
VALIDATION_ERROR_MSG = 'Validation failed'
VALIDATION_ERROR_CODE = 1007
INVALID_REFRESH_TOKEN_MSG = 'Invalid refresh token'
INVALID_REFRESH_TOKEN_CODE = 1008
INVALID_USER_ID_MSG = 'Invalid User ID'
INVALID_USER_ID_CODE = 1009
UNAUTHORIZED_ACCESS_MSG = 'Unauthorized access'
UNAUTHORIZED_ACCESS_CODE = 1010
PROVIDER_INVALID_MSG = 'Invalid or missing provider'
PROVIDER_INVALID_CODE = 1011
PROVIDER_INVALID_RESP_MSG = 'Invalid response from provider'
PROVIDER_INVALID_RESP_CODE = 1012
PROVIDER_INVALID_TOKEN_MSG = 'Could not validate token from provider'
PROVIDER_INVALID_TOKEN_CODE = 1013
MISSING_AUTH_CODE_MSG = 'Missing authorization code'
MISSING_AUTH_CODE_CODE = 1014
MISSING_PROVIDER_TOKEN_MSG = 'Missing provider\'s token'
MISSING_PROVIDER_TOKEN_CODE = 1015
MISSING_PROVIDER_USER_ID_MSG = 'Missing provider\'s user ID'
MISSING_PROVIDER_USER_ID_CODE = 1016
ACTIVATION_INVALID_TOKEN_MSG = 'Invalid or missing activation token'
ACTIVATION_INVALID_TOKEN = 1017
INVALID_OBJECT_ID_MSG = 'Invalid Object ID'
INVALID_OBJECT_ID_CODE = 1018
INVALID_PROJECT_MSG = 'Invalid Project ID'
INVALID_PROJECT_CODE = 1019
INVALID_TICKET_MSG = 'Invalid Ticket ID'
INVALID_TICKET_CODE = 1020
INVALID_SPRINT_MSG = 'Invalid Sprint ID'
INVALID_SPRINT_CODE = 1021
INVALID_COLUMN_MSG = 'Invalid Column ID'
INVALID_COLUMN_CODE = 1022
INVALID_PROJECT_MEMBER_MSG = 'Invalid Project Member ID'
INVALID_PROJECT_MEMBER_CODE = 1023
INVALID_ATTACHMENT_MSG = 'Invalid Attachment ID'
INVALID_ATTACHMENT_CODE = 1024
INVALID_COMMENT_MSG = 'Invalid Comment ID'
INVALID_COMMENT_CODE = 1025
INVALID_MEMBER_MSG = 'Invalid Member or Not Existing'
INVALID_MEMBER_CODE = 1039
INVALID_ALREADY_ADDED_MSG = 'Member Already Added'
INVALID_ALREADY_ADDED_CODE = 1040

ERROR_CODES = {
    REQUIRED_MSG: REQUIRED_CODE,
    INVALID_CREDENTIALS_MSG: INVALID_CREDENTIALS_CODE,
    INVALID_JSON_BODY_MSG: INVALID_JSON_BODY_CODE,
    INVALID_CONTENT_TYPE_MSG: INVALID_CONTENT_TYPE_CODE,
    MISSING_AUTH_HEADER_MSG: MISSING_AUTH_HEADER_CODE,
    INVALID_AUTH_HEADER_MSG: INVALID_AUTH_HEADER_CODE,
    INVALID_AUTH_TOKEN_MSG: INVALID_AUTH_TOKEN_CODE,
    VALIDATION_ERROR_MSG: VALIDATION_ERROR_CODE,
    INVALID_REFRESH_TOKEN_MSG: INVALID_REFRESH_TOKEN_CODE,
    INVALID_USER_ID_MSG: INVALID_USER_ID_CODE,
    UNAUTHORIZED_ACCESS_MSG: UNAUTHORIZED_ACCESS_CODE,
    PROVIDER_INVALID_MSG: PROVIDER_INVALID_CODE,
    PROVIDER_INVALID_RESP_MSG: PROVIDER_INVALID_RESP_CODE,
    PROVIDER_INVALID_TOKEN_MSG: PROVIDER_INVALID_TOKEN_CODE,
    MISSING_PROVIDER_TOKEN_MSG: MISSING_PROVIDER_TOKEN_CODE,
    MISSING_PROVIDER_USER_ID_MSG: MISSING_PROVIDER_USER_ID_CODE,
    MISSING_AUTH_CODE_MSG: MISSING_AUTH_CODE_CODE,
    ACTIVATION_INVALID_TOKEN_MSG: ACTIVATION_INVALID_TOKEN,
    INVALID_OBJECT_ID_MSG: INVALID_OBJECT_ID_CODE,
    INVALID_PROJECT_MSG: INVALID_PROJECT_CODE,
    INVALID_TICKET_MSG: INVALID_TICKET_CODE,
    INVALID_SPRINT_MSG: INVALID_SPRINT_CODE,
    INVALID_COLUMN_MSG: INVALID_COLUMN_CODE,
    INVALID_PROJECT_MEMBER_MSG: INVALID_PROJECT_MEMBER_CODE,
    INVALID_ATTACHMENT_MSG: INVALID_ATTACHMENT_CODE,
    INVALID_COMMENT_MSG: INVALID_COMMENT_CODE,
    INVALID_MEMBER_MSG: INVALID_MEMBER_CODE,
    INVALID_ALREADY_ADDED_MSG: INVALID_ALREADY_ADDED_CODE
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