Form widgets
============

.. class:: SimpleWidget

    Just renders a html snippet given to constructor.
    Can contain ``%(name)s`` and ``%(value)s``.


.. _CommaSeparatedInput:
.. class:: CommaSeparatedInput

    A text field for editing multiple values as comma separated list.
    Comes handy with ``IntegerArrayField``, ``BigIntegerArrayField`` and
    ``StringArrayField``.

.. class:: MultilineInput

    A textarea for editing multivalue fields.
    Most usefull with ``StringArrayField``.
