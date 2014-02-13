import django

# django.utils.simplejson is deprecated in Django 1.5
if django.VERSION >= (1, 5):
    import json
else:
    from django.utils import simplejson as json
