# -*- coding: utf-8 -*-
from django import forms
from django.utils.safestring import mark_safe


__all__ = ['SimpleWidget', 'CommaSeparatedInput', 'MultilineInput']


class SimpleWidget(forms.Widget):
    def __init__(self, format='%(value)s'):
        super(SimpleWidget, self).__init__()
        self.format = format

    def render(self, name, value, attrs=None):
        return mark_safe(self.format % {'name': name, 'value': value})


class CommaSeparatedInput(forms.TextInput):
    def _format_value(self, value):
        if isinstance(value, basestring):
            return value
        else:
            return ','.join(map(unicode, value))

    def value_from_datadict(self, data, files, name):
        value = data.get(name, '').strip()
        if value in ['', None]:
            return []
        return value.split(',')


class MultilineInput(forms.Textarea):
    def _format_value(self, value):
        if isinstance(value, basestring):
            return value
        else:
            return '\n'.join(value)
