#! -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from .views import ChannelCreateView
from .views import ChannelUpdateView
from .views import ChannelDeleteView
from .views import ChannelListView
from .views import publish

urlpatterns = patterns(
    '',
    url(r'^list/$', ChannelListView.as_view(), name='channel_list'),
    url(r'^create/$', ChannelCreateView.as_view(), name='channel_create'),
    url(r'^delete/(?P<pk>[\d]+)/$', ChannelDeleteView.as_view(), name='channel_delete'),
    url(r'^update/(?P<pk>[\d]+)/$', ChannelUpdateView.as_view(), name='channel_update'),
    url(r'^publish/$', publish, name='publish'),
)
