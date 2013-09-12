# -*- coding: utf-8 -*-
from functools import wraps
import re

from django.db import transaction, connections
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


def queryset_iterator(queryset, chunksize=1000):
    pk = 0
    try:
        last_pk = queryset.order_by('-pk')[0].pk
    except IndexError:
        raise StopIteration
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        # Use iterator to bypass queryset cache
        for row in queryset.filter(pk__gt=pk)[:chunksize].iterator():
            pk = row.pk
            yield row

def queryset_chunks(queryset, chunksize=1000):
    pk = 0
    while True:
        chunk = list(queryset.order_by('pk').filter(pk__gt=pk)[:chunksize])
        if chunk:
            pk = chunk[-1].pk
            yield chunk
        else:
            break


### A couple of low-level utilities

def fetch_all(sql, params=(), server='default'):
    return do_sql(sql, params, server).fetchall()

def fetch_row(sql, params=(), server='default'):
    return first(fetch_all(sql, params, server))

def fetch_col(sql, params=(), server='default'):
    return [row[0] for row in fetch_all(sql, params, server)]

def fetch_val(sql, params=(), server='default'):
    return first(fetch_row(sql, params, server))

def do_sql(sql, params=(), server='default'):
    cursor = connections[name].cursor()
    cursor.execute(sql, params)
    return cursor


def first(seq):
    return next(seq, None)
