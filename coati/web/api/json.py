from __future__ import absolute_import

from flask import json
from bson import json_util, SON

from coati.core import BaseDocument, CustomQuerySet

# dict of class/type -> func
_type_map = {}


class RegisterError(Exception):
    """
    Raised if a (un)register operation cannot be performed.
    """


class TransformError(Exception):
    """
    Raised if a transform operation cannot be performed on an object.
    """
    @property
    def message(self):
        return self.message


class JSONEncoder(json.JSONEncoder):
    """
    A JSON encoder that wraps the default behaviour
    """
    def _json_convert(self, obj):
        """Recursive helper method that converts BSON types so they can be
        converted into json.
        """
        string_types = (bytes, str)
        if hasattr(obj, 'iteritems') or hasattr(obj, 'items'):  # PY3 support
            return SON(((k, self._json_convert(v)) for k, v in obj.iteritems()))
        elif isinstance(obj, BaseDocument):
            return self._json_convert(transform(obj))
        elif hasattr(obj, '__iter__') and not isinstance(obj, string_types):
            return list((self._json_convert(v) for v in obj))
        try:
            return json_util.default(obj)
        except TypeError:
            return obj

    def default(self, obj):
        """
        Normal JSON encoding could not be performed, attempt to transform the
        object into something that can.
        """

        try:
            if isinstance(obj, CustomQuerySet):
                obj = list(obj)
            return self._json_convert(obj)
        except TransformError:
            return super(JSONEncoder, self).default(obj)


def unregister(klass):
    """
    Unregisters a previously registered klass.

    :param klass: The class object to be unregistered.
    """
    if klass not in _type_map:
        raise RegisterError('{!r} is not registered'.format(klass))

    del _type_map[klass]


def register(klass, func=None, replace=False):
    """
    Register a klass with a function to be called when instances of that class
    need to be transformed into a JSON encodable format.

    ``register`` can be used inline or as a decorator::

        @register(MyClass)
        def my_class_to_json(obj):
            pass

        # or

        register(MyClass, my_class_to_json)

        obj = MyClass()
        dumps(obj)

    In advanced cases, keyword arguments can be passed to the transforming
    function. This is useful for query optimising or controlling the transform.

    An example::

        class Foo(object):
            spam = 'eggs'

        @register(Foo)
        def foo_json(obj, include_bar=False):
            data = {
                'spam': obj.spam
            }

            if include_bar and hasattr(obj, 'bar'):
                data['bar'] = obj.bar

            return data

        # Would be used like:

        my_foo = Foo()

        my_foo.bar = 'bar'

        transform(my_foo, include_bar=True)

    :param klass: The class object to be transformed.
    :param func: The function to be called that must return the JSON encodable
        object. A single parameter is passed to the function, an instance of
        `klass`. In advanced cases, named parameters can be accepted.
    :param replace: Indicates whether the transforming function should be
        replaced or not, when it has already been registered.
    """
    def wrapped(func):
        if klass in _type_map:
            # If replacing is enabled, then unregister the klass, otherwise
            # raise an exception
            if replace:
                unregister(klass)
            else:
                raise RegisterError(
                    '{!r} is already registered'.format(klass)
                )

        _type_map[klass] = func

        return func

    if not func:
        return wrapped

    return wrapped(func)


def safe_register(klass, func=None):
    """
    Just a wrap around `register` with `replace` enabled.

    It can be used inline or as a decorator.

    :param klass: The class object to be transformed.
    :param func: The function to be called that must return the JSON encodable
        object. A single parameter is passed to the function, an instance of
        `klass`. In advanced cases, named parameters can be accepted.
    """
    return register(klass, func=func, replace=True)


def dumps(obj, **kwargs):
    """
    Return a JSON encoded serialised string of `obj`.

    See: http://flask.pocoo.org/docs/api/#flask.json.dumps
    """
    kwargs.setdefault('cls', JSONEncoder)

    return json.dumps(obj, **kwargs)


def loads(data, **kwargs):
    """
    Decode a JSON serialised string into a Python object.

    See: http://flask.pocoo.org/docs/api/#flask.json.loads
    """
    return json.loads(data, **kwargs)


def transform(obj, **kwargs):
    """
    Convert a complex ``obj`` into something that can be consumed by a JSON
    encoder.

    :param obj: The object to be transformed.
    :param kwargs: By default this is empty but allows custom calling of the
        function to pass to the transforming function.
    """
    global _type_map

    klass = getattr(obj, '__class__', None)

    if klass is None:
        raise TransformError('Cannot transform {!r}'.format(obj))

    func = _type_map.get(klass, None)

    if not func:
        raise TransformError('No registered type for {!r}'.format(obj))

    return func(obj, **kwargs)


def bulk_register(klasses_map):
    """
    Safely registers classes in bulk.

    :param klasses_map: a dictionary mapping classes to transforming functions.
    """
    for klass, func in klasses_map.items():
        safe_register(klass, func)

