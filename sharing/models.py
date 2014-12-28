# -*- coding: utf-8 -*-
from django.db import models

from settings.sharing_extensions import EXT_CHOICES
from core.models import TimeStampedModel


class SharingList(TimeStampedModel):

    """
    To store samples that users want to share.
    """

    STATUS_CHOICES = (
        (0, 'Queued'),
        (1, 'Processing'),
        (2, 'Failed'),
        (3, 'Success'),
        (4, 'Stop')
    )

    sample = models.ForeignKey('samples.Sample')
    extension = models.IntegerField(choices=EXT_CHOICES, null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return '{0} -> {1}'.format(self.sample.sha256, self.status)

    class Meta:
        ordering = ['-updated', '-created']
