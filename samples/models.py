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


class Malware(TimeStampedModel):
    link = models.TextField(null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True)
    size = models.IntegerField(null=True)
    md5 = models.CharField(max_length=32, null=True)
    sha1 = models.CharField(max_length=40, null=True)
    sha256 = models.CharField(max_length=64, null=True)
    sha512 = models.CharField(max_length=128, null=True)
    crc32 = models.IntegerField(max_length=255, null=True)
    ssdeep = models.CharField(max_length=255, null=True)
    desc = models.TextField(default='', null=True, blank=True)
    source = models.ForeignKey(SampleSource, null=True, blank=True)
    slug = models.SlugField(max_length=128)
    user = models.ForeignKey('auth.User', null=True, blank=True)

    def __unicode__(self):
        return self.sha256

    def get_absolute_url(self):
        return reverse_lazy('malware.list')

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.sha256)
        super(Malware, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created', '-updated']


class DownloadLog(TimeStampedModel):
    user = models.ForeignKey('auth.User')
    malware = models.CharField(max_length=128)
