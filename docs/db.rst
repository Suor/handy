Database
========

A couple of low-level utilities for those who tired of manually creating cursors.


.. function:: fetch_all(sql, server='default')

    Execute given sql and return all resulting rows.


.. function:: fetch_row(sql, server='default')

    Execute given sql and return one row.


.. function:: fetch_col(sql, server='default')

    Execute given sql and return list of values in first result column.


.. function:: fetch_val(sql, server='default')

    Execute given sql and return single resulting value::

        last_id = fetch_val('select max(id) from some_table')


.. function:: do_sql(sql, server='default')

    Execute given sql.
