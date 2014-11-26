# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.conf.urls import patterns

from views import NotificationList
from views import NotificationDetail


urlpatterns = patterns('',
    url(
        r'^list$',
        NotificationList,
        name='notification.list'
    ),
    url(
        r'^detail/(?P<pk>\d+)$',
        NotificationDetail,
        name='notification.detail'
    ),
)
