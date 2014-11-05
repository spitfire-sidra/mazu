# -*- coding: utf-8 -*-
from django.db import models


class TimeStampedModel(models.Model):

    """
    Common timestamp columns that models can extend.
    """

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
