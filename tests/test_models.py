# -*- coding: utf-8 -*-
import pytest
pytestmark = pytest.mark.django_db

from .models import Post, CategoryJSON, CategoryPickle


def test_stringarray():
    post = Post.objects.create(tags=['django', 'cool'])
    assert Post.objects.get(pk=post.pk).tags == post.tags

def test_stringarray_ru():
    post = Post.objects.create(tags=[u'привет'])
    assert Post.objects.get(pk=post.pk).tags == post.tags


def test_jsonfield():
    category = CategoryJSON.objects.create(info={'hey': 42})
    assert CategoryJSON.objects.get(pk=category.pk).info == category.info

def test_jsonfield():
    category = CategoryPickle.objects.create(info={'hey': 42})
    assert CategoryPickle.objects.get(pk=category.pk).info == category.info
