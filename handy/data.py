# -*- coding: utf-8 -*-
from collections import defaultdict
from itertools import ifilter, ifilterfalse, chain, izip, islice, repeat, tee, groupby


def split(test, coll):
    a, b = tee(coll)
    return ifilter(test, a), ifilterfalse(test, b)

def cluster(key, coll):
    result = defaultdict(list)
    for item in coll:
        result[key(item)].append(item)
    return result

def group(coll, key=None):
    return groupby(sorted(coll, key=key), key=key)

def with_prev(coll, key=None):
    if key is not None:
        coll = sorted(coll, key=key)
    a, b = tee(coll)
    return izip(a, chain([None], b))

def with_next(coll, key=None):
    if key is not None:
        coll = sorted(coll, key=key)
    a, b = tee(coll)
    return izip(a, padnone(skip(b)))

def skip(iterable, n=1):
    return islice(iterable, n, None)

def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.

    Useful for emulating the behavior of the built-in map() function.
    """
    return chain(iterable, repeat(None))
