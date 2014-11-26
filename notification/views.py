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

from core.mixins import LoginRequiredMixin
from notification.models import Notification


class NotificationListView(ListView, LoginRequiredMixin):

    """
    Displaying all notification.
    """

    model = Notification
    template_name = 'notification/list.html'
    paginate_by = 25

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class NotificationDetailView(DetailView, LoginRequiredMixin):

    """
    If an user click a link to a notification, then the notification will be
    marked to read.
    """

    model = Notification
    template_name = 'notification/detail.html'

    def get_object(self, *args, **kwargs):
        instance = self.model.objects.get(
            id=self.kwargs['pk'],
            user=self.request.user
        )

        # change column 'read' from False to True
        if instance.read == False:
            instance.read = True
            instance.save()
        return instance


NotificationList = NotificationListView.as_view()
NotificationDetail = NotificationDetailView.as_view()
