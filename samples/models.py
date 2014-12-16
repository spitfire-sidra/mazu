# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import URLValidator
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify

from core.models import TimeStampedModel


class SampleSource(TimeStampedModel):

    """
    SampleSource model stores information of sample sources.
    """

    name = models.CharField(max_length=255)
    link = models.URLField(null=True, blank=True)
    descr = models.TextField(null=True, blank=True)
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return '{0}'.format(self.name)

    def get_absolute_url(self):
        return reverse_lazy('source.detail',args=[self.pk])

    class Meta:
        ordering = ['name']
        # every user can create own sources
        unique_together = ('user', 'name')


class Filename(TimeStampedModel):

    """
    This models saves filename. A sample might have various filename,
    a filename might map to samples.
    """

    name = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User')

    class Meta:
        ordering = ['-created']


class Filetype(TimeStampedModel):

    """
    This models saves filetype.
    """

    filetype = models.CharField(max_length=255)
    detector = models.CharField(max_length=255)

    class Meta:
        ordering = ['filetype']
        unique_together = ('filetype', 'detector')


class Link(TimeStampedModel):

    """
    This model saves sample's links. Download links, report links or
    related links.
    """

    KIND_CHOICES = (
        (0, 'Download Link'),
        (1, 'Analysis Report Link'),
        (2, 'Other'),
    )

    url = models.TextField(validators=[URLValidator()])
    heading = models.CharField(max_length=255, null=True, blank=True)
    kind = models.IntegerField(max_length=2, choices=KIND_CHOICES, default=0)
    user = models.ForeignKey('auth.User')

    class Meta:
        ordering = ['kind', '-created']


class Sample(TimeStampedModel):

    """
    Sample model stores attributes of a sample
    """

    md5 = models.CharField(max_length=32)
    sha1 = models.CharField(max_length=40)
    sha256 = models.CharField(max_length=64)
    sha512 = models.CharField(max_length=128)
    ssdeep = models.CharField(max_length=255)
    size = models.IntegerField(default=0)
    crc32 = models.IntegerField(max_length=255)
    filetypes = models.ManyToManyField(Filetype, null=True, blank=True)
    filenames = models.ManyToManyField(Filename, null=True, blank=True)
    sources = models.ManyToManyField(SampleSource, null=True, blank=True)
    user = models.ForeignKey('auth.User')

    def __unicode__(self):
        return self.sha256

    def get_absolute_url(self):
        return reverse_lazy('sample.list')

    class Meta:
        ordering = ['-created', '-updated']


class Description(TimeStampedModel):

    """
    This models saves descriptions of a sample. A sample can have multiple
    descriptions, and a description might map to samples.
    """

    text = models.TextField()
    sample = models.ForeignKey(Sample)
    user = models.ForeignKey('auth.User')

    class Meta:
        ordering = ['-created']


class AccessLog(TimeStampedModel):

    """
    This models saves activity when a user download a samples.
    """

    sample = models.ForeignKey(Sample)
    user = models.ForeignKey('auth.User')

    class Meta:
        ordering = ['-created']
