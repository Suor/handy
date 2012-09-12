Functional tools
================

.. function:: @memoize

    Memoizes results of calls to a function.


    To be used as::

        from handy.funcs import memoize, cache

        @memoize
        def some_long_running_func(a, b, ...):
            ...

    Can be also used to cache calls to some external service, which are
    not supposed to change::

        @memoize
        def fetch_something(arg, ...):
            try:
                code, data = some_service_request(...)
                if code == REQ_OK:
                    return data
                else:
                    return None    # Nothing found, None result should be memoized
            except SomeServiceUnavailable:
                raise memoize.skip # return None and don't memoize it

.. function:: @cache(timeout=None)

    Caches results of function for ``timeout``. ``timeout`` could be integer number of seconds
    or ``timedelta``.
