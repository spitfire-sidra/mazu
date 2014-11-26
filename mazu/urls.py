# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from haystack.views import basic_search


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/$', login_required(basic_search)),
    url(r'^account/', include('account.urls')),
    url(r'^samples/', include('samples.urls')),
    url(r'^authkey/', include('authkey.urls')),
    url(r'^channel/', include('channel.urls')),
    url(r'^notification/', include('notification.urls')),
)
