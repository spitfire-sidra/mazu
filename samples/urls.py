# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from samples.views import download
from samples.views import SampleList
from samples.views import SampleUpload
from samples.views import SampleUpdate
from samples.views import SampleDelete
from samples.views import SampleDetail
from samples.views import SampleSourceList
from samples.views import SampleSourceCreate
from samples.views import SampleSourceUpdate
from samples.views import SampleSourceDelete
from samples.views import SampleSourceDetail


urlpatterns = patterns('',
    url(
        r'^source/list/$',
        SampleSourceList,
        name='source.list'
    ),
    url(
        r'^source/create/$',
        SampleSourceCreate,
        name='source.create'
    ),
    url(
        r'^source/update/(?P<pk>\d+)/$',
        SampleSourceUpdate,
        name='source.update'
    ),
    url(
        r'^source/delete/(?P<pk>\d+)/$',
        SampleSourceDelete,
        name='source.delete'
    ),
    url(
        r'^source/detail/(?P<pk>\d+)/$',
        SampleSourceDetail,
        name='source.detail'
    ),
)

urlpatterns += patterns('',
    url(
        r'^list/$',
        SampleList,
        name='sample.list'
    ),
    url(
        r'^upload/$',
        SampleUpload,
        name='malware.upload'
    ),
    url(
        r'^update/(?P<sha256>[\w]+)$',
        SampleUpdate,
        name='malware.update'
    ),
    url(
        r'^download/(?P<sha256>[\w]+)$',
        download,
        name='malware.download'
    ),
    url(
        r'^delete/(?P<sha256>[\w]+)$',
        SampleDelete,
        name='malware.delete'
    ),
    url(
        r'^profile/(?P<sha256>[\w]+)$',
        SampleDetail,
        name='malware.profile'
    ),
)
