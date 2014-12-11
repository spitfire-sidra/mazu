# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import URLValidator
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify

from core.models import TimeStampedModel


class Filename(TimeStampedModel):

    """
    This models saves filename. A sample might have various filename,
    a filename might map to samples.
    """

    name = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User')


class Description(TimeStampedModel):

    """
    This models saves descriptions of a sample. A sample can have multiple
    descriptions, and a description might map to samples.
    """

    text = models.TextField()
    user = models.ForeignKey('auth.User')


class Link(TimeStampedModel):

    """
    This model saves sample's links. Download links, report links or
    related links.
    """

    KIND_CHOICES = (
        (0, 'Download Link'),
        (1, 'Report Link'),
        (2, 'Related Link'),
    )

    url = models.TextField(validators=[URLValidator()])
    kind = models.IntegerField(max_length=2, choices=KIND_CHOICES, default=0)
    user = models.ForeignKey('auth.User')

    class Meta:
        ordering = ['kind', '-created']


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
    sources = models.ManyToManyField(SampleSource, null=True, blank=True)
    filenames = models.ManyToManyField(Filename, null=True, blank=True)
    descriptions = models.ManyToManyField(Description, null=True, blank=True)
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return self.sha256

    def get_absolute_url(self):
        return reverse_lazy('malware.list')

    class Meta:
        ordering = ['-created', '-updated']


class DownloadLog(TimeStampedModel):
    user = models.ForeignKey('auth.User')
    malware = models.CharField(max_length=128)
