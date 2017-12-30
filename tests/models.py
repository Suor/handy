from django.db import models
from handy.models import StringArrayField, JSONField, PickleField


class Post(models.Model):
    tags = StringArrayField()


class CategoryJ(models.Model):
    info = JSONField()


class CategoryJP(models.Model):
    info = JSONField(pickle=True)


class CategoryP(models.Model):
    info = PickleField()
