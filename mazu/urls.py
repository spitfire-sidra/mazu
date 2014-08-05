#! -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^malware/', include('malware.urls')),
    url(r'^authkey/', include('authkey.urls')),
    url(r'^channel/', include('channel.urls')),
)
