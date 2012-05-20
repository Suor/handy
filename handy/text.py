# -*- coding: utf-8 -*-
import re, string, random

from django.utils.safestring import mark_safe


def random_str(length=8, letters=string.ascii_letters + string.digits):
    """Generates random string of latin characters and digits"""
    return "".join(random.choice(letters) for x in range(length))


def formatnumber(value, splitter=' '):
    s = unicode(value)
    l = len(s)
    indexes = range(-(l + -l % 3), 0, 3)
    return mark_safe(splitter.join(s[i:i+3 or None] for i in indexes))


def formatnumber_html(value, splitter='<small>&nbsp;</small>'):
    return mark_safe(formatnumber(value, splitter))
