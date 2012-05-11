Mail utilities
==============

.. function:: render_to_email(email, template, [data], [request], [from_email], [attachment])

    Renders ``template`` with context constructed with help of ``request`` and filled with ``data``, then sends it to ``email``. An email template could contain email headers::

        from handy.mail import render_to_email

        def approve(...):
            article = ...
            render_to_email(article.author.email, 'approved.html', {'article': article})

        # in approved.html
        Content-Type: text/html
        Subject: Your article «{{ article.title }}» approved

        Hello, {{ article.author.username }}!<br><br>

        ....

.. function:: mail_admins(subject, message='', trace=True)

    Send an email to admins, optionally appends stack trace to message. Handy when you want get an exception email but still serve user request.
