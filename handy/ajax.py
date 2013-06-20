# -*- coding: utf-8 -*-
import re, datetime
from functools import wraps
import pytz

from django.http import HttpResponse
try:
    from django.utils.timezone import get_default_timezone
except ImportError:
    from django.conf import settings
    _default_timezone = pytz.timezone(settings.TIME_ZONE)
    get_default_timezone = lambda: _default_timezone

from .decorators import render_to_json


class AjaxException(Exception):
    def __init__(self, error='', **kwargs):
        defaults = {'success': False, 'error': error, 'data': {}}
        self.params = dict(defaults, **kwargs)

class Ajax(object):
    error = AjaxException

    def __call__(self, func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            try:
                data = func(request, *args, **kwargs)
                if isinstance(data, HttpResponse):
                    return data
                return {'success': True, 'data': data}
            except self.error, e:
                return e.params
        return render_to_json(default=encode_object)(wrapper)

    def catch(self, *exceptions):
        assert exceptions, 'at least one exception type is required'
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except self.error:
                    raise
                except exceptions, e:
                    error_name = camel_to_underscores(e.__class__.__name__)
                    error_text = e.args[0] if e.args else ''
                    raise self.error(error_name, error_text=error_text)
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

# TODO: add support for querysets and models
def encode_object(obj):
    if hasattr(obj, '__json__'):
        return obj.__json__()
    elif isinstance(obj, datetime.datetime):
        delta = to_default(obj) - EPOCH
        return {'_type': 'date', 'ms': int(delta.total_seconds() * 1000)}
    elif isinstance(obj, datetime.date):
        return datetime.datetime(*obj.timetuple()[:6])
    else:
        raise TypeError('%s is not JSON serializable' % obj.__class__.__name__)

def to_default(dt):
    if dt.tzinfo is None:
        return get_default_timezone().localize(dt)
    else:
        return dt.astimezone(get_default_timezone())

