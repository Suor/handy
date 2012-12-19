# -*- coding: utf-8 -*-
from itertools import chain, izip, tee


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

def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.

    Useful for emulating the behavior of the built-in map() function.
    """
    return chain(iterable, repeat(None))
