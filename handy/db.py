# -*- coding: utf-8 -*-
from functools import wraps

from django.db import transaction, connections


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
    cursor = connections[server].cursor()
    cursor.execute(sql, params)
    return cursor


def first(seq):
    return next(seq, None)
