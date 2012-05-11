.. _ajax:

Ajax wrap up
============

.. .. function:: @ajax

.. .. function:: @ajax.login_required


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
