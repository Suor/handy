# -*- coding: utf-8 -*-
try:
    import cPickle as pickle
except ImportError:
    import pickle

import re, datetime
from django.db import models
from django import forms
from django.core import exceptions, validators
from django.utils.text import capfirst
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from handy.forms import CommaSeparatedInput, MultilineInput
from handy.utils import get_module_attr


__all__ = ['AdditionalAutoField', 'AdditionalAutoFieldManager',
           'BigAutoField', 'IntegerArrayField', 'BigIntegerArrayField',
           'StringArrayField', 'BigIntegerField', 'JSONField']


class AdditionalAutoField(models.Field):
    """
    Дополнительный AutoField делает ещё одно auto поле не являющееся primary key
    Не поддерживается всеми бэкендами! viva la PostgreSQL :)

    Требуется использовать AdditionalAutoFieldManager в качестве базового менеджера, чтобы null не пропускались в базу:
        class MyModel(models.Model):
            _base_manager = AdditionalAutoFieldManager()
    """
    empty_strings_allowed = False
    def __init__(self, *args, **kwargs):
        kwargs['blank'] = True
        models.Field.__init__(self, *args, **kwargs)

    def get_internal_type(self):
        return "AutoField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return int(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be an integer."))

    def get_db_prep_value(self, value):
        if value is None:
            return None
        return int(value)

    def contribute_to_class(self, cls, name):
        models.Field.contribute_to_class(self, cls, name)

    def formfield(self, **kwargs):
        if self.primary_key:
            return None
        defaults = {'form_class': forms.IntegerField, 'widget': forms.HiddenInput}
        defaults.update(kwargs)
        return models.Field.formfield(self, **defaults)


class AdditionalAutoFieldManager(models.Manager):
    def _insert(self, values, **kwargs):
        # Значение по умолчанию выставлется базой
        values = [v for v in values if v[1] is not None or not isinstance(v[0], AdditionalAutoField)]
        return super(AdditionalAutoFieldManager, self)._insert(values, **kwargs)


class BigAutoField(models.AutoField):
    def __init__(self, verbose_name=None, name=None, external_sequence=False, **kwargs):
        self.external_sequence = external_sequence
        models.AutoField.__init__(self, verbose_name, name, **kwargs)

    def db_type(self, connection):
        return 'bigint' if self.external_sequence else 'bigserial'

    # Использует патч ForeignKey
    def rel_db_type(self, connection):
        return 'bigint'


class UntypedMultipleField(forms.Field):
    def __init__(self, *args, **kwargs):
        self.coerce = kwargs.pop('coerce', lambda val: val)
        super(UntypedMultipleField, self).__init__(*args, **kwargs)


class TypedMultipleField(UntypedMultipleField):
    def to_python(self, value):
        value = super(TypedMultipleField, self).to_python(value)
        if value not in validators.EMPTY_VALUES:
            try:
                value = map(self.coerce, value)
            except (ValueError, TypeError):
                raise exceptions.ValidationError(self.error_messages['invalid'])
        return value

class TypedMultipleChoiceField(TypedMultipleField, forms.MultipleChoiceField):
    def validate(self, value):
        pass


class ArrayField(models.Field):
    def validate(self, value, model_instance):
        # Это по-большей части скопировано с Field.validate
        # К сожалению приходится копипастить т.к. там неправильно проверяется
        # принадлежность к choices для многозначных полей
        if not self.editable:
            return

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages['null'])

        if not self.blank and value in validators.EMPTY_VALUES:
            raise exceptions.ValidationError(self.error_messages['blank'])

        # TODO: validate choices

    def formfield(self, **kwargs):
        if self.choices:
            # Тоже скопипащено из Field.formfield
            defaults = {
                'choices': self.choices,
                'coerce': self.coerce,
                'required': not self.blank,
                'label': capfirst(self.verbose_name),
                'help_text': self.help_text,
                'widget': forms.CheckboxSelectMultiple
            }
            defaults.update(kwargs)
            return TypedMultipleChoiceField(**defaults)
        else:
            defaults = {
                'form_class': TypedMultipleField,
                'coerce': self.coerce,
                'widget': CommaSeparatedInput,
            }
            defaults.update(kwargs)
            return super(ArrayField, self).formfield(**defaults)


class IntegerArrayField(ArrayField):
    default_error_messages = {
        'invalid': _(u'Enter only digits separated by commas.')
    }
    description = _("Array of integers")
    coerce = int

    def db_type(self, connection):
        return 'int[]'


class BigIntegerArrayField(IntegerArrayField):
    def db_type(self, connection):
        return 'bigint[]'

# Fix unicode arrays for postgresql_psycopg2 backend
try:
    import psycopg2
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
except ImportError:
    pass

class StringArrayField(ArrayField):
    description = _("Array of strings")
    coerce = unicode

    def __init__(self, verbose_name=None, **kwargs):
        kwargs.setdefault('max_length', 127)
        super(StringArrayField, self).__init__(verbose_name, **kwargs)

    def db_type(self, connection):
        return 'varchar(%s)[]' % self.max_length


# Функции для кодирования/декодирования объектов в json
def default_decode((cls, data)):
    cls = get_module_attr(cls)
    obj = cls.__new__(cls)
    obj.__dict__.update(data['__data__'])
    return obj

def encode_object(obj):
    if hasattr(obj, '__json__'):
        data = obj.__json__()
        if isinstance(data, tuple):
            decode, data = data
        else:
            decode = default_decode
            data = ('%s.%s' % (obj.__class__.__module__, obj.__class__.__name__), data)

        if callable(decode):
            decode = '%s.%s' % (decode.__module__, decode.__name__)

        return {
            '__decode__': decode,
            '__data__': data
        }
    else:
        return dict(__pickled__=pickle.dumps(obj))

def decode_object(d):
    if '__decode__' in d:
        return get_module_attr(d['__decode__'])(d['__data__'])
    elif '__pickled__' in d:
        return pickle.loads(str(d['__pickled__']))
    else:
        return d

class JSONField(models.TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""
        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value, object_hook=decode_object)
        except ValueError:
            pass

        return value

    def get_prep_value(self, value):
        """Convert our JSON object to a string before we save"""
        if value == "" or value is None:
            return None

        #if isinstance(value, dict):
        value = json.dumps(value, default=encode_object, ensure_ascii=False, separators=(',',':'))

        return super(JSONField, self).get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.Field,
        }
        defaults.update(kwargs)
        defaults['widget'] = JSONTextarea
        return super(JSONField, self).formfield(**defaults)


class JSONTextarea(forms.Textarea):
    def value_from_datadict(self, data, files, name):
        value = data.get(name, '').strip()
        if value in ['', None]:
            return {}
        return json.loads(value)

    def render(self, name, value, attrs=None):
        return super(JSONTextarea, self).render(name, json.dumps(value), attrs=attrs)



class BigIntegerField(models.IntegerField):
    def db_type(self):
        # только для mysql и postgres
        return "bigint"

    def get_internal_type(self):
        return "BigIntegerField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(
                _("This value must be a long integer."))


# Прописываем правила для South, пустые так как новых, неунаследованных атрибутов у нас нет
try:
    from south.modelsinspector import add_introspection_rules
    rules = [
        ((BigAutoField, ), [], {"external_sequence": ["external_sequence", {"default": False}]}),
        ((StringArrayField, ), [], {"max_length": ["max_length", {}]}),
    ]
    add_introspection_rules(rules, ["^handy\.models\.fields\."])
except ImportError:
    pass
