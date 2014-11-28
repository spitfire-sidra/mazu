#! -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from views import ChannelCreateView
from views import ChannelUpdateView
from views import ChannelDeleteView
from views import ChannelListView
from views import QueueListView


urlpatterns = patterns(
    '',
    url(r'^list/$', ChannelListView.as_view(), name='channel.list'),
    url(r'^create/$', ChannelCreateView.as_view(), name='channel.create'),
    url(r'^delete/(?P<pk>[\d]+)/$', ChannelDeleteView.as_view(), name='channel.delete'),
    url(r'^update/(?P<pk>[\d]+)/$', ChannelUpdateView.as_view(), name='channel.update'),
    url(r'^queue/$', QueueListView.as_view(), name='queue.list'),
)
