Model fields
============

Here come some custom model fields mostly designed to work with PostgreSQL.

.. class:: AdditionalAutoField

    Additional autoincremented field which is not primary key.

    Should be used with ``AdditionalAutoFieldManager``::

        from handy.models import AdditionalAutoField, AdditionalAutoFieldManager

        class MyModel(models.Model):
            num = AdditionalAutoField()

            _base_manager = AdditionalAutoFieldManager()


.. class:: BigAutoField

    An ``AutoField`` but uses bigint. If ``external_sequence`` argument is set to true
    then sequence is not created with field.


.. class:: ArrayField

    A base for all array fields. If ``choices`` argument is given then renders to multiple checkboxes in form else to :ref:`CommaSeparatedInput <CommaSeparatedInput>`.


.. class:: IntegerArrayField

    An array of integers.


.. class:: BigIntegerArrayField

    An array of big integers.


.. class:: StringArrayField(ArrayField)

    An array of strings. Has ``max_length`` parameter for a maximum length of each string.


.. class:: JSONField

    A field for storing arbitrary jsonifyable data.
