# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from sharing.views import SharingForm


urlpatterns = patterns('',
    url(
        r'^sample/(?P<sha256>[\w]+)$',
        SharingForm,
        name='sharing.form'
    )
)
