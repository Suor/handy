# -*- coding: utf-8 -*-
from functools import wraps
import simplejson as json
from datetime import datetime

from django.conf import settings
from django.template import loader, RequestContext
from django.http import HttpResponse
from django.utils.http import http_date


def template_guess(func):
    template_dir = func.__module__.replace('.views', '').replace('.', '/')
    return template_dir + '/' + func.__name__ + getattr(settings, 'TEMPLATE_DEFAULT_EXTENSION', '.html')


def render_dict(request, output):
    # Составляем доп. параметры
    template = output.pop('TEMPLATE')
    kwargs = dict((k.lower(), output.pop(k)) for k in ('STATUS', 'CONTENT_TYPE') if k in output)
    # Рендерим шаблон и заворачиваем в ответ
    rendered = loader.render_to_string(template, output, RequestContext(request))
    return HttpResponse(rendered, **kwargs)


def render_to(template=None):
    """
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
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError

def render_to_json(ensure_ascii=True, default=_json_default):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if isinstance(response, str):
                json_data = response
            else:
                if settings.DEBUG:
                    json_data = json.dumps(response, sort_keys=True, indent=4, ensure_ascii=False, default=default)
                else:
                    json_data = json.dumps(response, ensure_ascii=ensure_ascii, separators=(',',':'), default=default)
            return HttpResponse(json_data, content_type='text/plain; charset=utf-8')
            #return HttpResponse(json_data, mimetype='application/json')
        return wrapper
    return decorator


def last_modified(func):
    @wraps(func)
    def wrap(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        response['Last-Modified'] = http_date()
        return response
    return wrap
