# Use psycopg2cffi for PyPy
try:
    import psycopg2  # noqa
except ImportError:
    from psycopg2cffi import compat
    compat.register()
