Middleware
==========

.. class:: StripWhitespace

    A middleware that strips whitespace from html responses to make them smaller.
    Doesn't strip newlines in order to not break any embeded javascript.

    Just add ``handy.middleware.StripWhitespace`` to your ``MIDDLEWARE_CLASSES``.


