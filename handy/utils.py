# -*- coding: utf-8 -*-
from datetime import datetime
from importlib import import_module


__all__ = ['obj_dump', 'get_module_attr', 'cached_property', 'get_or_none']


from django.db.models.fields.related import ForeignKey
ForeignKey.__dump__ = lambda self: 'ForeignKey(%s.%s -> %s.%s)' % (self.model, self.attname, self.rel.to, self.rel.field_name)

# Thing removed in Django 1.9
try:
    from django.db.models.sql.where import Constraint
    Constraint.__dump__ = lambda self: 'Constraint(%s.%s)' % (self.alias, self.col)
except ImportError:
    pass


def obj_dump(obj, indent=0, seen=None):
    if seen is None:
        seen = set()
    result = []
    if obj is None or isinstance(obj, (str, int, long, float, bool, dict, set, datetime)) or callable(obj):
        result.append(repr(obj))
    elif isinstance(obj, unicode):
        result.append("u'" + obj.encode('utf8') + "'")
    elif isinstance(obj, (list, tuple)) and not obj:
        result.append(repr(obj))
    elif hasattr(obj, '__dump__'):
        result.append(obj.__dump__())
    elif id(obj) in seen:
        result.append('<SEEN_OBJECT>')
    else:
        seen.add(id(obj))
        if isinstance(obj, (list, tuple)):
            result.append('[\n' if isinstance(obj, list) else '(\n')
            for item in obj:
                result.append('%s,' % obj_dump(item, indent=indent+4, seen=seen))
            result.append(']' if isinstance(obj, list) else ')')
        else:
            result.append(repr(obj) + '\n')
            for attr, value in obj.__dict__.iteritems():
                result.append('%s: %s,' % (attr, obj_dump(value, indent=indent+4, seen=seen)))

    result = result[0] + "\n".join(' ' * indent + i for i in result[1:])
    return result


def get_module_attr(path):
    """
    Возвращает атрибут модуля, переданный в виде строки 'module.other.AttrName'.
    Удобно для получения класса по строке импорта.
    При отсутствии атрибута возвращает None.
    """
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
        return getattr(mod, attr, None)
    except ImportError:
        return None


class cached_property(object):
    """
    Decorator that converts a method with a single self argument into
    a property cached on the instance.
    """
    # NOTE: implementation borrowed from Django.
    # NOTE: we use fget, fset and fdel attributes to mimic @property.
    fset = fdel = None

    def __init__(self, fget):
        self.fget = fget
        self.__doc__ = getattr(fget, '__doc__')

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        res = instance.__dict__[self.fget.__name__] = self.fget(instance)
        return res


def get_or_none(cls, **cond):
    try:
        return cls.objects.get(**cond)
    except cls.DoesNotExist:
        return None
