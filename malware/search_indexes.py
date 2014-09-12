# -*- coding: utf-8 -*-
import datetime
from haystack import indexes
from models import Malware


class MalwareIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    user = indexes.CharField(model_attr='user')
    md5 = indexes.CharField(model_attr='md5')
    sha1 = indexes.CharField(model_attr='sha1')
    sha256 = indexes.CharField(model_attr='sha256')
    sha512 = indexes.CharField(model_attr='sha512')
    created = indexes.DateTimeField(model_attr='created')

    def get_model(self):
        return Malware

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created__lte=datetime.datetime.now())
