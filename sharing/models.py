# -*- coding: utf-8 -*-
from django.db import models
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse_lazy

from core.models import TimeStampedModel


class HPFeedsChannel(TimeStampedModel):

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
        return "HPFeedsChannel-#{0}-{1}".fromat(self.id, self.name)

    def split_chans(self, text):
        """
        Split channels by comma. Remove empty items and strip spaces.

        For example:
        >>> [x.strip(' ') for x in 'a, b,    c,d,,,'.split(',') if x]
        ['a', 'b', 'c', 'd']
        """
        return [x.strip(' ') for x in text.split(',') if x]

    def get_pubchans(self):
        return self.split_chans(self.pubchans)

    def get_subchans(self):
        return self.split_chans(self.subchans)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(HPFeedsChannel, self).save(*args, **kwargs)

    class Meta:
        ordering = ['host', 'port']
        unique_together = ('user', 'name')


class HPFeedsPubQueue(TimeStampedModel):

    """
    This model stores all samples that are waiting for publishing.
    """

    sample = models.ForeignKey('samples.Sample')
    channel = models.ForeignKey(HPFeedsChannel)
    published = models.BooleanField(default=False)

    def __unicode__(self):
        return 'HPFeedsPubQueue-#{0}'.format(self.id)
