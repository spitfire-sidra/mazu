# -*- coding: utf-8 -*-
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse_lazy
from django.db import models

from core.models import TimeStampedModel


class Channel(TimeStampedModel):
    owner = models.ForeignKey('auth.User', null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    pubchans = models.TextField(null=True, blank=True)
    subchans = models.TextField(null=True, blank=True)
    ident = models.TextField()
    secret = models.TextField(null=True, blank=True)
    slug = models.SlugField()

    def __unicode__(self):
        return self.pubchans

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(Channel, self).save(*args, **kwargs) 

    class Meta:
        ordering = ['host', 'port']
        unique_together = ('owner', 'name')
