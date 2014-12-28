#! -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from views import HPFeedsChannelCreateView
from views import HPFeedsChannelUpdateView
from views import HPFeedsChannelDeleteView
from views import HPFeedsChannelListView
from views import HPFeedsPubQueueListView


urlpatterns = patterns('',
    url(
        r'^list/$',
        HPFeedsChannelListView.as_view(),
        name='channel.list'
    ),
    url(
        r'^create/$',
        HPFeedsChannelCreateView.as_view(),
        name='channel.create'
    ),
    url(
        r'^publish/(?P<sha256>[\w]+)$',
        HPFeedsChannelCreateView.as_view(),
        name='sharing.via.hpfeeds'
    ),
    url(
        r'^delete/(?P<pk>[\d]+)/$',
        HPFeedsChannelDeleteView.as_view(),
        name='channel.delete'
    ),
    url(
        r'^update/(?P<pk>[\d]+)/$',
        HPFeedsChannelUpdateView.as_view(),
        name='channel.update'
    ),
    url(
        r'^queue/$',
        HPFeedsPubQueueListView.as_view(),
        name='queue.list'
    ),
)
