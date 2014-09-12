# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.conf.urls import patterns

from views import NotificationListView
from views import NotificationDetailView


urlpatterns = patterns(
    '',
    url(r'^list$', NotificationListView.as_view(), name='notification.list'),
    url(r'^detail/(?P<pk>\d+)$',NotificationDetailView.as_view(), name='notification.detail'),
)
