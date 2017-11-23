# -*- coding: utf-8 -*-
import re
from functools import wraps

from django.http import HttpResponse

from .decorators import render_to_json


__all__ = ['ajax']


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
            except self.error as e:
                return e.params
        return render_to_json()(wrapper)

    def catch(self, *exceptions):
        assert exceptions, 'at least one exception type is required'
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except self.error:
                    raise
                except exceptions as e:
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
