# -*- coding: utf-8 -*-
from django.http import Http404
from django.http import HttpResponseForbidden
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from core.mixins import LoginRequiredMixin
from core.mongodb import connect_gridfs
from sharing.forms import ChannelForm
from sharing.models import Channel
from sharing.models import Queue


class ChannelCreateView(CreateView, LoginRequiredMixin):
    model = Channel
    form_class = ChannelForm
    template_name = 'channel/create.html'
    success_url = reverse_lazy('channel.list')

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(**kwargs)

    def form_valid(self, form):
        # save the user of channel
        form.instance.user = self.request.user
        return super(ChannelCreateView, self).form_valid(form)


class ChannelListView(ListView, LoginRequiredMixin):
    model = Channel
    template_name = 'channel/list.html'
    context_object_name = 'channels'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class ChannelUpdateView(UpdateView):
    model = Channel
    template_name = 'channel/update.html'
    form_class = ChannelForm
    success_url = reverse_lazy('channel.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise HttpResponseForbidden
        return super(ChannelUpdateView, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(**kwargs)


class ChannelDeleteView(DeleteView):
    model = Channel
    template_name = 'channel/delete.html'
    success_url = reverse_lazy('channel.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise HttpResponseForbidden
        return super(ChannelDeleteView, self).dispatch(*args, **kwargs)


class QueueListView(ListView, LoginRequiredMixin):
    model = Queue
    template_name = 'queue/list.html'
    context_object_name = 'queues'

    def get_queryset(self):
        return self.model.objects.filter(malware__user=self.request.user)

