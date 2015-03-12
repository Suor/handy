View decorators
===============

.. decorator:: render_to([template])

    Decorator for Django views that sends returned dict to ``render_to_response()`` function.
    If ``template`` is not specified then it is guessed from module and view names.

    .. note:: If view doesn't return dict then decorator does nothing  -- handy when you need
              conditionally return redirect.

    There are a number of keys in view result dictionary which have special meaning:

    TEMPLATE
        override template used to render view

    STATUS
        set HTTP status code other than 200

    CONTENT_TYPE
        set `Content-Type` of view response

    Most common usage::

        from handy.decorators import render_to

        # in module smth.views
        @render_to()
        def foo(request):
            return {'bar': Bar.objects.all()}

        # equals to
        def foo(request):
            return render_to_response('smth/foo.html',
                                      {'bar': Bar.objects.all()},
                                      context_instance=RequestContext(request))


.. _paginate_decorator:
.. decorator:: paginate(name, ipp)

    Paginates any queryset or sequence value returned in ``name`` key in response dict. Also, populates ``page`` key in response dict if not already used. It passes through if result is not ``HttpResponse`` or value is not a sequence, so you can return redirects and ``None``
    conveniently::

        from handy.decorators import render_to, paginate

        @render_to()
        @paginate('series', 10)
        def search(request):
            q = request.GET.get('q')
            return {
                'columns': get_series_columns(),
                'series': search_series_qs(q) if q else None,
            }

    Here is a Bootstrap and jinja2 snippet for pagination (just drop all the parentheses to convert it to django):

    .. code-block:: jinja

        {% if page and page.has_other_pages() %}
        <nav>
          <ul class="pagination">
            {% if page.has_previous() %}
            <li>
              <a href="?p={{ page.previous_page_number() }}" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
              </a>
            </li>
            {% endif %}
            {% for p in page.paginator.page_range %}
              <li{% if p == page.number %} class="active"{% endif %}>
                <a href="?p={{ p }}">{{ p }}</a>
              </li>
            {% endfor %}
            {% if page.has_next() %}
            <li>
              <a href="/?p={{ page.next_page_number() }}" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
              </a>
            </li>
            {% endif %}
          </ul>
        </nav>
        {% endif %}


.. _render_to_json:
.. decorator:: render_to_json(ensure_ascii=True, default=_json_default)

    Serializes view result to json and wraps into ``HttpResponse``. Arguments are forwarded to
    ``json.dumps()``.

    An example of ajax action handler::

        from handy.decorators import render_to_json

        @render_to_json()
        def enable_post(request):
            if not request.user.is_authenticated():
                return {'success': False, 'error': 'login_required'}

            try:
                post = Post.objects.get(pk=request.GET['id'])
            except Post.DoesNotExist:
                return {'success': False, 'error': 'no_post'}

            post.enabled = True
            post.save()

            return {'success': True}

    Or a JSON datasource::

        @render_to_json()
        def posts_by_tag(request, tag=None):
            posts = Post.object.values().filter(tag=tag)
            return {'success': True, 'data': list(posts)}

    For higher order tool see :ref:`ajax`


.. decorator:: last_modified

    Adds ``Last-Modified`` header with current time to view response.
    Meaned to be used with ``CommonMiddleware`` and caching to produce
    ``403 Not Modified`` responses::

        from django.views.decorators.cache import cache_page
        from handy.decorators import last_modified

        @cache_page(60 * 15)
        @last_modified
        def my_view(request):
            ...
