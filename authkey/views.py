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

from .models import AuthKey


class AuthKeyCreateView(CreateView):
    model = AuthKey
    template_name = 'authkey/create.html'
    success_url = reverse_lazy('authkey_list')
    fields = ['ident', 'secret', 'pubchans', 'subchans']


class AuthKeyListView(ListView):
    model = AuthKey
    template_name = 'authkey/list.html'
    context_object_name = 'authkeys'


class AuthKeyUpdateView(UpdateView):
    model = AuthKey
    template_name = 'authkey/update.html'
    success_url = reverse_lazy('authkey_list')
    fields = ['ident', 'secret', 'pubchans', 'subchans']


class AuthKeyDeleteView(DeleteView):
    model = AuthKey
    template_name = 'authkey/delete.html'
    success_url = reverse_lazy('authkey_list')
