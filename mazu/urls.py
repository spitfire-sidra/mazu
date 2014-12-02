# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from haystack.views import basic_search


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'account.views.auth'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/$', login_required(basic_search)),
    url(r'^account/', include('account.urls')),
    url(r'^samples/', include('samples.urls')),
    url(r'^brokers/', include('brokers.urls')),
    url(r'^channel/', include('sharing.urls')),
    url(r'^notification/', include('notification.urls')),
)
