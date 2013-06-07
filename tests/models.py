from django.db import models
from handy.models import StringArrayField


class Post(models.Model):
    tags = StringArrayField()
