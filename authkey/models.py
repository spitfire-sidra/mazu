# -*- coding: utf-8 -*-
from django.db import models


class Log(models.Model):
    data = models.TextField()

    def __unicode__(self):
        return self.data

    class Meta:
        ordering = ['-id']


class ConnStats(models.Model):
    ak = models.TextField() # auth key
    uid = models.ForeignKey('auth.User', null=True, blank=True) # user
    data = models.TextField()

    def __unicode__(self):
        return self.uid

    class Meta:
        ordering = ['uid']


class AuthKey(models.Model):
	owner = models.ForeignKey('auth.User', null=True, blank=True) # user
	ident = models.TextField()
	secret = models.TextField(null=True, blank=True)
	pubchans = models.TextField(null=True, blank=True)
	subchans = models.TextField(null=True, blank=True)

	def __unicode__(self):
		return self.pubchans

	class Meta:
		ordering = ['ident']
