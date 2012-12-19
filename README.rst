Handy
=====

A collection of different tools, shortcuts, decorators, form and model fields
to make your django life easier.

Installation
-------------

::

    pip install handy


Overview
--------

Here are quick overview of what you can do with handy.
You can also read `full docs <http://handy.readthedocs.org/>`_.

Avoid ``HttpResponse`` and ``render_to_response()`` biolerplate with ``@render_to()`` decorator.
This one will render result dict to ``'app_name/foo.html'``::

    @render_to()
    def foo(request):
        return {
            'bar': Bar.objects.all()
            # You can easily override default template, content type,
            # status code and add cookies to response:
            'STATUS': 410,
            'CONTENT_TYPE': 'text/plain'
        }

Easy JSON responders with ``@render_to_json()`` decorator::

    @render_to_json()
    def posts_by_tag(request, tag=None):
        posts = Post.object.values().filter(tag=tag)
        return list(posts)

And higher order ``@ajax`` decorator to handle more complex asynchronous actions::

    @ajax
    @ajax.login_required
    @ajax.catch(Post.DoesNotExist)
    def enable_post(request):
        post = Post.objects.get(pk=request.GET['id'])

        if post.author != request.user:
            raise ajax.error('permission_denied')

        post.enabled = True
        post.save()


Send emails rendered from templates::

    render_to_email(article.author.email, 'approved.html', {'article': article})

A collection of model fields with accompanying form fields and widgets. Most notably diffrent array
fields to store array of values or choices::

    DAYS = zip(range(7), 'Sun Mon Tue Wed Thu Fri Sat'.split())

    class Company(models.Model):
        phones = StringArrayField('Phone numbers', blank=True, default='{}')
        workdays = IntegerArrayField('Work days', choices=DAYS)

    company = Company(phones=['234-5016', '516-2314'], workdays=[1,2,3,4])
    company.save()

In model form ``phones`` field would be represented as ``CommaSeparatedInput`` and
``workdays`` as multiple checkboxes::

    class CompanyForm(forms.ModelForm):
        class Meta:
            model = Company

A handy ``@cached_property`` utility::

    class UserProfile(models.Model):
        phones = models.ManyToManyField(Phone)

        ...

        @cached_property
        def public_phones(self):
            # this queryset will be constructed only once, thanks to @cached_property
            return self.phones.filter(public=True)

And a middleware to make your html output slimmer by stripping out unnecessary spaces::

    MIDDLEWARE_CLASSES = (
        ...
        'handy.middleware.StripWhitespace',
    )

And more:

- generic master slave database router with a couple of utilities
- simple logger wrap up
- ``JSONField``, ``AdditionalAutoField`` and ``BigAutoField``
- and a couple of text and debugging utilities

NOTE: functional tools, namely ``@memoize`` and ``@cache``, moved to
`funcy <https://github.com/Suor/funcy>`_


How you can help
----------------

- give me any feedback. What bits are most useful? What can be added or changed?
- bring your ideas and/or code that can make all our django experience more fun


TODO
----

- translate comments for model fields
- docs for db, text and just utils
- add support for querysets and models in JSON decorators
- db_fetch(), db_do(), db_tuples() and such primitives
