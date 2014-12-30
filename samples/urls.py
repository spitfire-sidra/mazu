# -*- coding: utf-8 -*-
from django.conf.urls import patterns
from django.conf.urls import url

from samples.views import download
from samples.views import SampleList
from samples.views import SampleUpload
from samples.views import SampleDelete
from samples.views import SampleDetail
from samples.views import SampleUpdate
from samples.views import FilenameDelete
from samples.views import FilenameRemove
from samples.views import FilenameAppend
from samples.views import HyperlinkAppend
from samples.views import HyperlinkRemove
from samples.views import SourceAppend
from samples.views import DescriptionCreate
from samples.views import DescriptionDelete
from samples.views import DescriptionUpdate
from samples.views import SourceList
from samples.views import SourceCreate
from samples.views import SourceUpdate
from samples.views import SourceDelete
from samples.views import SourceDetail
from samples.views import SourceRemove


urlpatterns = patterns('',
    url(
        r'^source/list/$',
        SourceList,
        name='source.list'
    ),
    url(
        r'^source/create/$',
        SourceCreate,
        name='source.create'
    ),
    url(
        r'^source/update/(?P<pk>\d+)/$',
        SourceUpdate,
        name='source.update'
    ),
    url(
        r'^source/delete/(?P<pk>\d+)/$',
        SourceDelete,
        name='source.delete'
    ),
    url(
        r'^source/detail/(?P<pk>\d+)/$',
        SourceDetail,
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
        name='sample.upload'
    ),
    url(
        r'^download/(?P<sha256>[\w]+)$',
        download,
        name='sample.download'
    ),
    url(
        r'^delete/(?P<sha256>[\w]+)$',
        SampleDelete,
        name='sample.delete'
    ),
    url(
        r'^profile/(?P<sha256>[\w]+)$',
        SampleDetail,
        name='sample.detail'
    ),
    url(
        r'^update/(?P<sha256>[\w]+)$',
        SampleUpdate,
        name='sample.update'
    ),
    url(
        r'^filename/delete/(?P<pk>\d+)$',
        FilenameDelete,
        name='filename.delete'
    ),
    url(
        r'^filename/remove/(?P<sha256>[\w]+)/(?P<filename_pk>\d+)$',
        FilenameRemove,
        name='filename.remove'
    ),
    url(
        r'^filename/append/(?P<sha256>[\w]+)$',
        FilenameAppend,
        name='filename.append'
    ),
    url(
        r'^hyperlink/append/(?P<sha256>[\w]+)$',
        HyperlinkAppend,
        name='hyperlink.append'
    ),
    url(
        r'^hyperlink/remove/(?P<sha256>[\w]+)/(?P<hyperlink_pk>\d+)$',
        HyperlinkRemove,
        name='hyperlink.remove'
    ),
    url(
        r'^source/append/(?P<sha256>[\w]+)$',
        SourceAppend,
        name='source.append'
    ),
    url(
        r'^source/remove/(?P<sha256>[\w]+)/(?P<source_pk>\d+)$',
        SourceRemove,
        name='source.remove'
    ),
    url(
        r'^descr/create/(?P<sha256>[\w]+)$',
        DescriptionCreate,
        name='descr.create'
    ),
    url(
        r'^descr/delete/(?P<pk>\d+)$',
        DescriptionDelete,
        name='descr.delete'
    ),
    url(
        r'^descr/update/(?P<pk>\d+)$',
        DescriptionUpdate,
        name='descr.update'
    ),
)
