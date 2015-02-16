# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from rest_framework import routers

from api.views import UserViewSet
from api.views import SampleViewSet


router = routers.DefaultRouter()
router.register(r'account', UserViewSet)
router.register(r'sample', SampleViewSet)

# urlpatterns for API endpoints
urlpatterns = patterns('',
    url(r'^v1/', include(router.urls)),
)
