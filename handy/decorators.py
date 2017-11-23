# -*- coding: utf-8 -*-
from functools import wraps

import django
from django.conf import settings
from django.template import loader, RequestContext
from django.http import HttpRequest, HttpResponse
from django.utils.http import http_date

from handy.cross import json
from django.core.serializers.json import DjangoJSONEncoder


__all__ = ['render_to', 'render_to_json', 'last_modified', 'paginate']


def template_guess(func):
    template_dir = func.__module__.replace('.views', '').replace('.', '/')
    return template_dir + '/' +                                                     \
           func.__name__ + getattr(settings, 'TEMPLATE_DEFAULT_EXTENSION', '.html')


def render_dict(request, output):
    # extracting hook keys
    template = output.pop('TEMPLATE')
    kwargs = dict((k.lower(), output.pop(k)) for k in ('STATUS', 'CONTENT_TYPE') if k in output)
    # rendering remplate and wrapping it into HttpResponse
    if django.VERSION >= (1, 8):
        rendered = loader.render_to_string(template, output, request=request)
    else:
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


def render_to_json(ensure_ascii=True, cls=DjangoJSONEncoder):
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
                    json_data = json.dumps(response, cls=cls, ensure_ascii=False,
                        sort_keys=True, indent=4)
                else:
                    json_data = json.dumps(response, cls=cls, ensure_ascii=ensure_ascii,
                        separators=(',',':'))
            return HttpResponse(json_data, content_type='application/json')
        return wrapper
    return decorator


def last_modified(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        response['Last-Modified'] = http_date()
        return response
    return wrapper


from .shortcuts import paginate as _paginate

def paginate(name, ipp, *extra):
    # Also works as shortcut
    if isinstance(name, HttpRequest):
        return _paginate(name, ipp, *extra)
    assert not extra, "There should be exactly 2 arguments for @paginate"

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output

            if sequence_like(output[name]):
                output[name] = _paginate(request, output[name], ipp)
            if 'page' not in output:
                output['page'] = output[name]

            return output

        return wrapper
    return decorator

def sequence_like(seq):
    cls = seq.__class__
    return hasattr(cls, '__getitem__') and (hasattr(cls, 'count') or hasattr(cls, '__len__'))
