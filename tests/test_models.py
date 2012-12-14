# -*- coding: utf-8 -*-
import pytest
pytestmark = pytest.mark.django_db


from .models import Post

def test_stringarray():
    post = Post.objects.create(tags=['django', 'cool'])
    assert Post.objects.get(pk=post.pk).tags == post.tags

def test_stringarray_ru():
    post = Post.objects.create(tags=[u'привет'])
    assert Post.objects.get(pk=post.pk).tags == post.tags
