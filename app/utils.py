from flask import make_response


__author__ = 'gastonrobledo'


def output_json(obj, code, headers=None):
    """
    This is needed because we need to use a custom JSON converter
    that knows how to translate MongoDB types to JSON.
    """

    try:
        resp = make_response(obj, code)
        resp.headers.extend(headers or {})
    except Exception as ex:
        # logged into the log.txt file
        pass

    return resp










