# -*- coding: utf-8 -*-
import pytest
pytestmark = pytest.mark.django_db

from .models import Post, CategoryJ, CategoryJP, CategoryP


def test_stringarray():
    post = Post.objects.create(tags=['django', 'cool'])
    assert Post.objects.get(pk=post.pk).tags == post.tags

def test_stringarray_ru():
    post = Post.objects.create(tags=[u'привет'])
    assert Post.objects.get(pk=post.pk).tags == post.tags


def test_jsonfield():
    category = CategoryJ.objects.create(info={'hey': 42})
    assert CategoryJ.objects.get(pk=category.pk).info == category.info

    with pytest.raises(TypeError):
        CategoryJ.objects.create(info={'hey': object})

def test_jsonpfield():
    category = CategoryJP.objects.create(info={'hey': object})
    assert CategoryJP.objects.get(pk=category.pk).info == {'hey': object}

def test_picklefield():
    category = CategoryP.objects.create(info={'hey': 42})
    assert CategoryP.objects.get(pk=category.pk).info == category.info
