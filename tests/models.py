from django.db import models
from handy.models import StringArrayField, JSONField, PickleField


class Post(models.Model):
    tags = StringArrayField()


class CategoryJSON(models.Model):
    info = JSONField()


class CategoryPickle(models.Model):
    info = PickleField()
