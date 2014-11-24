# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from samples.views import download
from samples.views import SampleList
from samples.views import SampleUpload
from samples.views import SampleUpdate
from samples.views import SampleDelete
from samples.views import SampleDetail
from samples.views import SamplePublish
from samples.views import SampleSourceList
from samples.views import SampleSourceUpdate
from samples.views import SampleSourceDelete
from samples.views import SampleSourceCreate


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
        r'^source/update/(?P<slug>[\w]+)/$',
        SampleSourceUpdate,
        name='source.update'
    ),
    url(
        r'^source/delete/(?P<slug>[\w]+)/$',
        SampleSourceDelete,
        name='source.delete'
    ),
)

urlpatterns += patterns('',
    url(
        r'^list/$',
        SampleList,
        name='malware.list'
    ),
    url(
        r'^upload/$',
        SampleUpload,
        name='malware.upload'
    ),
    url(
        r'^download/(?P<slug>[\w]+)/$',
        download,
        name='malware.download'
    ),
    url(
        r'^list/(?P<slug>[\w]+)/$',
        SampleList,
        name='malware.source.filter'
    ),
    url(
        r'^profile/(?P<slug>[\w]+)/$',
        SampleDetail,
        name='malware.profile'
    ),
    url(
        r'^delete/(?P<slug>[\w]+)/$',
        SampleDelete,
        name='malware.delete'
    ),
    url(
        r'^update/(?P<slug>[\w]+)/$',
        SampleUpdate,
        name='malware.update'
    ),
    url(
        r'^publish/(?P<slug>[\w]*)/$',
        SamplePublish,
        name='malware.publish'
    ),
)
