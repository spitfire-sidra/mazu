# -*- coding: utf-8 -*-
import logging

from django.http import Http404
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from models import AuthKey


REQUIRED_PERMISSIONS = ['authkey.add_authkey', 'authkey.change_authkey', 'authkey.delete_authkey']


def can_access_authkey(user):
    if user.is_superuser or user.has_perms(REQUIRED_PERMISSIONS):
        return True
    else:
        return False


class AuthKeyCreateView(CreateView):
    model = AuthKey
    template_name = 'authkey/create.html'
    success_url = reverse_lazy('authkey.list')
    fields = ['ident', 'secret', 'pubchans', 'subchans']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if can_access_authkey(self.request.user):
            return super(AuthKeyCreateView, self).dispatch(*args, **kwargs)
        else:
            raise Http404


class AuthKeyListView(ListView):
    model = AuthKey
    template_name = 'authkey/list.html'
    context_object_name = 'authkeys'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if can_access_authkey(self.request.user):
            return super(AuthKeyListView, self).dispatch(*args, **kwargs)
        else:
            raise Http404


class AuthKeyUpdateView(UpdateView):
    model = AuthKey
    template_name = 'authkey/update.html'
    success_url = reverse_lazy('authkey.list')
    fields = ['ident', 'secret', 'pubchans', 'subchans']

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if can_access_authkey(self.request.user):
            return super(AuthKeyUpdateView, self).dispatch(*args, **kwargs)
        else:
            raise Http404


class AuthKeyDeleteView(DeleteView):
    model = AuthKey
    template_name = 'authkey/delete.html'
    success_url = reverse_lazy('authkey.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if can_access_authkey(self.request.user):
            return super(AuthKeyDeleteView, self).dispatch(*args, **kwargs)
        else:
            raise Http404
