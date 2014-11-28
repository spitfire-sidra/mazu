# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse_lazy

from core.models import TimeStampedModel


class Channel(TimeStampedModel):

    """
    This model stores channels that used for HPFeeds.
    """

    name = models.CharField(max_length=255)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    pubchans = models.TextField()
    subchans = models.TextField()
    identity = models.TextField()
    secret = models.TextField()
    default = models.BooleanField(default=False)
    slug = models.SlugField()
    user = models.ForeignKey('auth.User')
    source = models.ForeignKey('samples.SampleSource', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Channel, self).save(*args, **kwargs)

    class Meta:
        ordering = ['host', 'port']
        unique_together = ('user', 'name')


class Queue(TimeStampedModel):
    malware = models.ForeignKey('samples.Sample')
    channel = models.ForeignKey(Channel)
    published = models.BooleanField(default=False)

    def __unicode__(self):
        return 'QUEUE-{}'.format(self.id)
