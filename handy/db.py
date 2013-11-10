# -*- coding: utf-8 -*-
from functools import wraps
from operator import itemgetter
from collections import namedtuple
from contextlib import closing, contextmanager

from django.db import transaction, connections


__all__ = ('commit_on_success_on',
           'queryset_iterator', 'queryset_chunks',
           'fetch_all', 'fetch_row', 'fetch_col', 'fetch_val', 'do_sql',
           'fetch_named', 'fetch_named_row')


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
    with db_execute(sql, params, server) as cursor:
        return cursor.fetchall()

def fetch_row(sql, params=(), server='default'):
    with db_execute(sql, params, server) as cursor:
        return cursor.fetchone()

def fetch_col(sql, params=(), server='default'):
    return [row[0] for row in fetch_all(sql, params, server)]

def fetch_val(sql, params=(), server='default'):
    return silent_first(fetch_row(sql, params, server))

def do_sql(sql, params=(), server='default'):
    with db_execute(sql, params, server) as _:
        pass

# A low level cursor access context manager
@contextmanager
def db_execute(sql, params=(), server='default'):
    with closing(connections[server].cursor()) as cursor:
        cursor.execute(sql, params)
        yield cursor


def fetch_named(sql, params=(), server='default'):
    with db_execute(sql, params, server) as cursor:
        rec_class = _row_namedtuple(cursor)
        return map(rec_class._make, cursor.fetchall())

def fetch_named_row(sql, params=(), server='default'):
    with db_execute(sql, params, server) as cursor:
        rec_class = _row_namedtuple(cursor)
        return rec_class._make(cursor.fetchone())

def _row_namedtuple(cursor):
    field_names = map(itemgetter(0), cursor.description)
    return namedtuple('TableRow', field_names)


def silent_first(seq):
    try:
        return seq[0]
    except (IndexError, TypeError):
        return None

