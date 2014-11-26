# -*- coding: utf-8 -*-
from django.db import models

from core.models import TimeStampedModel


class Notification(TimeStampedModel):

    """
    The column 'read' would be Fasle by default. If an user viewed
    a notification, the column 'read' must be set to True.
    """

    user = models.ForeignKey('auth.User')
    subject = models.CharField(max_length=255)
    message = models.TextField(max_length=255)
    read = models.BooleanField(default=False)

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ['-id', 'read', 'created']
        get_latest_by = 'updated'
