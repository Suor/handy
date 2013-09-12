Database
========

A couple of low-level utilities for those who tired of manually creating cursors.


.. function:: fetch_all(sql, params=(), server='default')

    Execute given sql and return all resulting rows.


.. function:: fetch_row(sql, params=(), server='default')

    Execute given sql and return one row.


.. function:: fetch_col(sql, params=(), server='default')

    Execute given sql and return list of values in first result column.


.. function:: fetch_val(sql, params=(), server='default')

    Execute given sql and return single resulting value::

        last_id = fetch_val('select max(id) from some_table')


.. function:: do_sql(sql, params=(), server='default')

    Execute given sql with given params.



.. function:: queryset_iterator(queryset, chunksize=1000)

    Iterate over a Django Queryset ordered by the primary key.

    This method loads a maximum of chunksize (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. It also bypasses django queryset cache.

    Note that ordered querysets not supported.


.. function:: queryset_chunks(queryset, chunksize=1000)

    Returns iterator yielding chunks of django queryset. Takes care not to load everything at once.
