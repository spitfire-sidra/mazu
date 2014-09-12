# -*- coding: utf-8 -*-
from django.db import models

from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    user = models.ForeignKey('auth.User')
    subject = models.CharField(max_length=255)
    message = models.TextField(max_length=255)
    read = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-id', 'read']
        get_latest_by = 'updated'
