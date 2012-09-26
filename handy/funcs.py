# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime, timedelta
from functools import wraps


class SkipMemoization(Exception):
    pass


def memoize(func):
    cache = {}

    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            try:
                cache[args] = func(*args)
            except SkipMemoization, e:
                return e.args[0] if e.args else None

        return cache[args]
    return wrapper
memoize.skip = SkipMemoization


def cache(timeout):
    if isinstance(timeout, int):
        timeout = timedelta(seconds=timeout)

    def decorator(func):
        cache = {}

        @wraps(func)
        def wrapper(*args):
            if args in cache:
                result, timestamp = cache[args]
                if datetime.now() - timestamp < timeout:
                    return result
                else:
                    del cache[args]

            result = func(*args)
            cache[args] = result, datetime.now()
            return result

        def invalidate(*args):
            cache.pop(args)
        wrapper.invalidate = invalidate

        def invalidate_all():
            cache.clear()
        wrapper.invalidate_all = invalidate_all

        return wrapper
    return decorator


def limit_error_rate(fails=None, timeout=None, exception=None):
    if isinstance(timeout, int):
        timeout = timedelta(seconds=timeout)

    def decorator(func):
        func.fails = 0
        func.blocked = None

        @wraps(func)
        def wrapper(*args, **kwargs):
            if func.blocked and datetime.now() - func.blocked < timeout:
                raise exception

            try:
                result = func(*args, **kwargs)
            except:
                func.fails += 1
                if func.fails >= fails:
                    func.blocked = datetime.now()
                raise
            else:
                func.fails = 0
                func.blocked = None
                return result
        return wrapper
    return decorator


def log(print_func=print):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_words = list(args) + ['%s=%s' % t for t in kwargs.items()]
            print_func('Call %s(%s)' % (func.__name__, ', '.join(map(str, arg_words))))
            result = func(*args, **kwargs)
            print_func('-> %s' % repr(result))
            return result
        return wrapper
    return decorator


def log_errors(print_func=print):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception, e:
                print_func('%s: %s in %s' % (e.__class__.__name__, e, func.__name__))
                raise
        return wrapper
    return decorator


def silent(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            return None
    return wrapper
