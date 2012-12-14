from django.db import models
from handy.models import StringArrayField


class Post(models.Model):
    # title = models.CharField(max_length=128)
    tags = StringArrayField()
