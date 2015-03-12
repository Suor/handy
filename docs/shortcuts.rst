Shortcuts
=========

.. function:: paginate(request, queryset, ipp)

    Paginates `queryset` and returns a :class:`~django:django.core.paginator.Page` object.
    Current page number is extracted from ``request.GET['p']`` if exists and coerced to available pages::

        from handy.shortcuts import paginate

        def search(request, ...):
            items = Item.objects.filter(...)
            page = paginate(request, items, 10)
            # ...
