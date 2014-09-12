# -*- coding: utf-8 -*-
import os
import json

from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import RequestContext
from django.contrib import messages

from models import Notification


class NotificationListView(ListView):
    model = Notification
    template_name = 'notification/list.html'
    paginate_by = 25

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NotificationListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(
            user=self.request.user
        )


class NotificationDetailView(DetailView):
    model = Notification
    template_name = 'notification/detail.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NotificationDetailView, self).dispatch(*args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = self.model.objects.get(
            id=self.kwargs['pk'],
            user=self.request.user
        )
        # Change read from False to True
        if obj.read == False:
            obj.read = True
            obj.save()
        return obj 
