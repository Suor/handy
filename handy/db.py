# -*- coding: utf-8 -*-
from functools import wraps
import re

from django.db import transaction
from django.conf import settings


class MasterSlaveRouter(object):
    read_from_master = False # A global flag to switch read requests to master

    _replication_sets_re = set(re.compile(s[0]) for s in settings.DATABASE_SETS_RE)
    _cache = set()
    def _is_replicated(self, model):
        table_name = model._meta.db_table
        if table_name in self._cache:
            return True
        for regex in self._replication_sets_re:
            if regex.search(table_name):
                self._cache.add(table_name)
                return True
        return False

    def db_for_read(self, model, **hints):
        if self.read_from_master:
            return self.db_for_write(model, **hints)
        return 'default'

    def db_for_write(self, model, **hints):
        return settings.DEFAULT_MASTER if self._is_replicated(model) else 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, db, model):
        return True


def read_from_master(func):
    """
    Decorator which switches any read db requests done in function to master.
    Should be used with handy.db.MasterSlaveRouter.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        previous_state = MasterSlaveRouter.read_from_master
        MasterSlaveRouter.read_from_master = True
        try:
            return func(*args, **kwargs)
        except:
            raise
        finally:
            MasterSlaveRouter.read_from_master = previous_state
    return wrapper


def commit_on_success_on(*databases):
    databases = set(databases)
    def decorator(func):
        for db in databases:
            func = transaction.commit_on_success(db)(func)
        return wraps(func)(func)
    return decorator
