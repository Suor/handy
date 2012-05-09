# -*- coding: utf-8 -*-
from functools import wraps
import simplejson as json
from datetime import datetime

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import loader, RequestContext
from django.http import HttpResponse
from django.utils.http import http_date
import traceback


def template_guess(function):
    template_dir = function.__module__.replace('.views', '').replace('.', '/')
    return template_dir + '/' + function.__name__ + getattr(settings, 'TEMPLATE_DEFAULT_EXTENSION', '.html')


def render_dict(request, output):
    # Составляем доп. параметры
    template = output.pop('TEMPLATE')
    kwargs = dict((k.lower(), output.pop(k)) for k in ('STATUS', 'CONTENT_TYPE') if k in output)
    # Рендерим шаблон и заворачиваем в ответ
    rendered = loader.render_to_string(template, output, RequestContext(request))
    return HttpResponse(rendered, **kwargs)


def render_to(template=None):
    """
    Decorator for Django views that sends returned dict to render_to_response function.
    Based on django-annoying @render_to() decorator

    Template name can be decorator parameter or TEMPLATE item in returned dictionary.
    RequestContext always added as context instance.
    If view doesn't return dict then decorator simply returns output.

    Parameters:
     - template: template name to use

    Examples:
    # 1. Template name in decorator parameters

    @render_to('template.html')
    def foo(request):
        bar = Bar.object.all()
        return {'bar': bar}

    # equals to
    def foo(request):
        bar = Bar.object.all()
        return render_to_response('template.html',
                                  {'bar': bar},
                                  context_instance=RequestContext(request))


    # 2. Template name as TEMPLATE item value in return dictionary

    @render_to()
    def foo(request, category):
        template_name = '%s.html' % category
        return {'bar': bar, 'TEMPLATE': template_name}

    #equals to
    def foo(request, category):
        template_name = '%s.html' % category
        return render_to_response(template_name,
                                  {'bar': bar},
                                  context_instance=RequestContext(request))

    # 3. Guess template name from function and app names
    # TEMPLATE item value in return dictionary should be absent or none to enable guessing

    # in module smth.views
    @render_to()
    def foo(request):
        return {'bar': Bar.objects.all()}

    #equals to
    def foo(request):
        return render_to_response('smth/foo.html',
                                  {'bar': Bar.objects.all()},
                                  context_instance=RequestContext(request))


    render_to can set cookies from COOKIES item in returned dictionary.
    COOKIES must be a list of dicts or a dict, each dict is passed as **kwargs to
    response.set_cookie method.

    Example:
        return {'COOKIES': dict(key='MyCookie', value='MyValue')}
    or
        return {'COOKIES': (dict(key='cookie1', value='value1'), dict(key='cookie2', value='value2'))}

    One can also use STATUS and CONTENT_TYPE special keys.
    """
    def decorator(function):
        template_default = template or template_guess(function)

        @wraps(function)
        def wrapper(request, *args, **kwargs):
            output = function(request, *args, **kwargs)
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
            #return HttpResponse(json, mimetype='application/json')
        return wrapper
    return decorator


def last_modified(func):
    @wraps(func)
    def wrap(request, *a, **kw):
        response = func(request, *a, **kw)
        response['Last-Modified'] = http_date()
        return response
    return wrap
