# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.views import logout_then_login

urlpatterns = patterns('',
    url(
        r'^$',
        'account.views.index'
    ),
    url(
        r'^login$',
        'account.views.auth'
    ),
    url(
        r'^logout', 
        logout_then_login,
        name='user.logout'
    ),
    url(
        r'^signup$',
        'account.views.signup'
    ),
    url(
        r'^passwd$',
        'account.views.passwd',
        name='user.passwd'
    ),
)
