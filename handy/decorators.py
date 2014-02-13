# -*- coding: utf-8 -*-
from functools import wraps
from datetime import datetime

from django.conf import settings
from django.template import loader, RequestContext
from django.http import HttpResponse
from django.utils.http import http_date

from handy.cross import json


def template_guess(func):
    template_dir = func.__module__.replace('.views', '').replace('.', '/')
    return template_dir + '/' +                                                     \
           func.__name__ + getattr(settings, 'TEMPLATE_DEFAULT_EXTENSION', '.html')


def render_dict(request, output):
    # extracting hook keys
    template = output.pop('TEMPLATE')
    kwargs = dict((k.lower(), output.pop(k)) for k in ('STATUS', 'CONTENT_TYPE') if k in output)
    # rendering remplate and wrapping it into HttpResponse
    rendered = loader.render_to_string(template, output, RequestContext(request))
    return HttpResponse(rendered, **kwargs)


def render_to(template=None):
    """
    Renders view result to template. Inspired by `@render_to()` decorator
    from django-annoying package.
    """
    def decorator(func):
        template_default = template or template_guess(func)

        @wraps(func)
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output

            output.setdefault('TEMPLATE', template_default)
            response = render_dict(request, output)
            if 'COOKIES' in output:
                cookies = (output['COOKIES'],) if isinstance(output['COOKIES'], dict) else output['COOKIES']
                for i in cookies:
                    response.set_cookie(**i)
            return response

        return wrapper
    return decorator


def _json_default(obj):
    # TODO: unify json func here, in ajax, and the one used by JSONField
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError

def render_to_json(ensure_ascii=True, default=_json_default):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if isinstance(response, HttpResponse):
                return response
            elif isinstance(response, str):
                json_data = response
            else:
                if settings.DEBUG:
                    json_data = json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False, default=default)
                else:
                    json_data = json.dumps(response, ensure_ascii=ensure_ascii, separators=(',',':'), default=default)
            return HttpResponse(json_data, mimetype='application/json; charset=utf-8')
        return wrapper
    return decorator


def last_modified(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        response['Last-Modified'] = http_date()
        return response
    return wrapper
