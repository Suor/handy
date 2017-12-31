Model fields
============

Here come some custom model fields mostly designed to work with PostgreSQL.


.. class:: IntegerArrayField
           BigIntegerArrayField
           StringArrayField(max_length=None)

    An arrays of integers, big integers or strings. Most useful to store different array
    fields to store array of values or choices::

        DAYS = zip(range(7), 'Sun Mon Tue Wed Thu Fri Sat'.split())

        class Company(models.Model):
            phones = StringArrayField('Phone numbers', blank=True, default=lambda: [])
            workdays = IntegerArrayField('Work days', choices=DAYS)

        company = Company(phones=['234-5016', '516-2314'], workdays=[1,2,3,4])
        company.save()

    In model form ``phones`` field would be represented as :class:`CommaSeparatedInput` and
    ``workdays`` as multiple checkboxes::

        class CompanyForm(forms.ModelForm):
            class Meta:
                model = Company # No additional magic needed


.. class:: JSONField(pickle=False)

    A field for storing arbitrary jsonifyable data. Set ``pickle`` to True to pickle anything non-jsonifyable.


.. class:: PickleField

    A field for storing arbitrary picklable data.


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


