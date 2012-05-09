# -*- coding: utf-8 -*-
import logging, logging.handlers

from django.conf import settings


def get_logger(name, level=logging.INFO, format='[%(asctime)s] %(message)s', handler=None, filename=None):
    new_logger = logging.getLogger(name)
    new_logger.setLevel(level)

    if not handler:
        filename = filename or '%s/logs/%s.log' % (settings.HOME_DIR, name)
        handler = logging.FileHandler(filename)

    handler.setFormatter(logging.Formatter(format))
    new_logger.addHandler(handler)

    return new_logger


if hasattr(settings, 'LOG_FILENAME') and not logger:
    handler = logging.handlers.TimedRotatingFileHandler(settings.LOG_FILENAME, when = 'midnight')
    logger = get_logger('default', handler=handler)
