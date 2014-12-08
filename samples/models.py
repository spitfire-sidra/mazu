# -*- coding: utf-8 -*-
from django.db import models
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify

from core.models import TimeStampedModel


class SampleSource(TimeStampedModel):

    """
    SampleSource model stores information of sample sources.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField()
    link = models.URLField(null=True, blank=True)
    descr = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return reverse_lazy('source.list')

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(SampleSource, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        # every user can create own sources
        unique_together = ('user', 'name')


class Sample(TimeStampedModel):

    """
    Sample model stores attributes of a sample
    """

    md5 = models.CharField(max_length=32)
    sha1 = models.CharField(max_length=40)
    sha256 = models.CharField(max_length=64)
    sha512 = models.CharField(max_length=128)
    ssdeep = models.CharField(max_length=255)
    filetype = models.CharField(max_length=255, default='Unknown')
    size = models.IntegerField(default=0)
    crc32 = models.IntegerField(max_length=255)
    source = models.ForeignKey(SampleSource, blank=True, null=True)
    slug = models.SlugField(max_length=128)
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return self.sha256

    def get_absolute_url(self):
        return reverse_lazy('malware.list')

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.sha256)
        super(Sample, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created', '-updated']


class SampleExtraInfo(TimeStampedModel):

    """
    SampleExtraInfo model stores extra information about a sample.
    """

    sample = models.ForeignKey(Sample)
    name = models.CharField(max_length=255, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    descr = models.TextField(default='', null=True, blank=True)


class DownloadLog(TimeStampedModel):
    user = models.ForeignKey('auth.User')
    malware = models.CharField(max_length=128)
