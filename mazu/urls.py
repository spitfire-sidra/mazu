#! -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url
from django.contrib.auth.views import logout_then_login
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'auth.views.index'),
    url(r'^auth$', 'auth.views.auth'),
    url(r'^signup$', 'auth.views.signup'),
    url(r'^passwd$', 'auth.views.passwd', name='user.passwd'),
    url(r'^logout',  logout_then_login, name='user.logout'),
)


urlpatterns += patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^malware/', include('malware.urls')),
    url(r'^authkey/', include('authkey.urls')),
    url(r'^channel/', include('channel.urls')),
)
