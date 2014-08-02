#! -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from .views import AuthKeyCreateView
from .views import AuthKeyUpdateView
from .views import AuthKeyDeleteView
from .views import AuthKeyListView


urlpatterns = patterns(
    '',
    url(r'^list/$', AuthKeyListView.as_view(), name='authkey_list'),
    url(r'^create/$', AuthKeyCreateView.as_view(), name='authkey_create'),
    url(r'^delete/(?P<pk>[\d]+)/$', AuthKeyDeleteView.as_view(), name='authkey_delete'),
    url(r'^update/(?P<pk>[\d]+)/$', AuthKeyUpdateView.as_view(), name='authkey_update'),
)
