.. _ajax:

Ajax wrap up
============

An example of ajax handler and JSON datasource::

    from handy.ajax import ajax

    @ajax
    @ajax.login_required
    @ajax.catch(Post.DoesNotExist)
    def enable_post(request):
        post = Post.objects.get(pk=request.GET['id'])

        if post.author != request.user:
            # sends {"success": false, "error": "permission_denied"}
            raise ajax.error('permission_denied')

        post.enabled = True
        post.save()
        # sends {"success": true, "data": null} on successful return

    @ajax
    def posts_by_tag(request, tag=None):
        # sends {"success": true, "data": [{...}, {...}, ...]}
        return Post.object.values().filter(tag=tag)


In addition to serialization usual values ``@ajax`` can serialize datetimes, dates and any objects with ``__json__()`` method.

You can use :download:`this JSON reviver <../handy/static/reviver.js>` on client side to deserialize all of these in browser.


See also :ref:`@render_to_json() <render_to_json>`

