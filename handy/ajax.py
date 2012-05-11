# -*- coding: utf-8 -*-
import re, datetime
from functools import wraps
import pytz

from .decorators import render_to_json


class AjaxException(Exception):
    def __init__(self, message='', **kwargs):
        defaults = {'success': False, 'error': message, 'data': {}}
        self.params = dict(defaults, **kwargs)


class Ajax(object):
    error = AjaxException

    def __call__(self, func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                data = func(request, *args, **kwargs)
                return {'success': True, 'data': data}
            except self.error, e:
                return e.params
        return render_to_json(default=encode_object)(wrapper)

    def catch(self, exception):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except self.error:
                    raise
                except exception, e:
                    return {'success': False,
                            'error': camel_to_underscores(exception.__name__),
                            'error_text': e.args[0]}
            return wrapper
        return decorator

    def login_required(self, func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_anonymous():
                raise self.error('login_required')
            else:
                return func(request, *args, **kwargs)
        return wrapper

ajax = Ajax()


def camel_to_underscores(name):
    words = re.findall(r'[A-Z][a-z0-9]+', name)
    return '_'.join(w.lower() for w in words)


### Encoding object to json
from pytz.tzinfo import DstTzInfo
DstTzInfo.__json__ = lambda self: self.zone

UTC = pytz.timezone('UTC')
EPOCH = datetime.datetime(1970,1,1,0,0,0, tzinfo=UTC)

def encode_object(obj):
    if hasattr(obj, '__json__'):
        return obj.__json__()
    elif isinstance(obj, datetime.datetime):
        delta = timezone.to_default(obj) - EPOCH
        return {'_type': 'date', 'ms': int(delta.total_seconds() * 1000)}
    elif isinstance(obj, datetime.date):
        return datetime.datetime(*obj.timetuple()[:6])
    else:
        raise TypeError('%s is not JSON serializable' % obj.__class__.__name__)
