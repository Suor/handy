# -*- coding: utf-8 -*-
import re, sys, traceback
from smtplib import SMTPRecipientsRefused

import django
from django.conf import settings
from django.core.mail import EmailMessage, mail_admins as django_mail_admins
from django.template import loader, RequestContext
from django.core.files.uploadedfile import InMemoryUploadedFile


__all__ = ['render_to_email', 'mail_admins']


def parse_email_data(content):
    lines = content.splitlines()

    subject, content_subtype = None, None
    headers = {}

    for i, line in enumerate(lines):
        # Headers read?
        if not line and subject:
            lines = lines[i+1:]
            break

        m = re.search(r'^([\w-]+): (.+)', line.strip())
        if not m:
            raise ValueError('Email subject required\nPrepend email content with "Subject:\s<subject>\\n\\n"')
        name, value = m.groups()

        if name == 'Subject':
            subject = value
        elif name == 'Content-Type':
            m = re.search('^text/([\w-]+)', value)
            if not m:
                raise ValueError('Erroneous email content type %s' % value)
            content_subtype = m.group(1)
        else:
            headers[name] = value
    return subject, content_subtype, headers, '\n'.join(lines)


def render_to_email(email, template_name, data=None, request=None, from_email=None, attachment=None):
    if not email:
        return

    if django.VERSION >= (1, 8):
        content = loader.render_to_string(template_name, context=data, request=request)
    else:
        context = RequestContext(request) if request else None
        content = loader.render_to_string(template_name, data or {}, context)

    subject, content_subtype, headers, email_text = parse_email_data(content)

    if not isinstance(email, (list, tuple)):
        email = [email]

    message = EmailMessage(subject, email_text, from_email, email, headers=headers)
    if content_subtype:
        message.content_subtype = content_subtype

    if attachment:
        add_attach = lambda uploadedFile: message.attach(uploadedFile.name, uploadedFile.read(), uploadedFile.content_type)

        if isinstance(attachment, list):
            for attach in attachment:
                if isinstance(attach, InMemoryUploadedFile):
                    add_attach(attach)
        elif isinstance(attachment, InMemoryUploadedFile):
            add_attach(attachment)

    try:
        message.send()
    except SMTPRecipientsRefused:
        pass

    if settings.DEBUG:
        print(u'To: %s' % ', '.join(message.to))
        print(u'From: %s' % message.from_email)
        print(u'Subject: %s' % message.subject)
        print(message.body)


def mail_admins(subject, message='', trace=True):
    if trace:
        exc_info = sys.exc_info()
        if exc_info:
            message += ("\n\n" if message else '') + ''.join(traceback.format_exception(*exc_info))
    django_mail_admins(subject, message, fail_silently=True)
