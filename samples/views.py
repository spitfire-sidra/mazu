# -*- coding: utf-8 -*-
import os
import logging

from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import RequestContext
from django.views.generic.edit import FormMixin

from models import Malware
from models import SampleSource
from models import DownloadLog
from forms import MalwareUploadForm
from forms import MalwarePublishForm
from forms import MalwareUpdateForm
from forms import MalwareFilterForm
from forms import SourceForm
from utils import compute_hashes
from utils import compute_ssdeep
from utils import get_uploaded_file_info
from channel.models import Channel
from channel.models import Queue
from core.mongodb import connect_gridfs
from core.mongodb import get_compressed_file
from core.mongodb import delete_file


logger = logging.getLogger(__name__)


@login_required
def download(request, slug):
    try:
        malware = get_compressed_file('sha256', slug)
    except Exception as e:
        logger.debug(e)
        messages.error(request, 'Oops! We got an error!')
        return render(request, 'error.html')
    else:
        if malware:
            response = HttpResponse(malware.read())
            response['Content-Disposition'] = 'attachment; filename={}.zip'.format(slug)
            response['Content-Type'] = 'application/x-zip'
            DownloadLog(user=request.user, malware=slug).save()
            return response
        else:
            raise Http404


class MalwarePublishView(FormView):
    template_name = 'malware/publish.html'
    form_class = MalwarePublishForm
    success_url = reverse_lazy('malware.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MalwarePublishView, self).dispatch(*args, **kwargs)

    def get_initial(self):
        try:
            sha256 = self.kwargs['slug']
        except:
            return {}
        else:
            return {'malware': sha256}

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(
            **kwargs
        )

    def form_valid(self, form):
        form.save()
        return super(MalwarePublishView, self).form_valid(form)


class MalwareUploadView(FormView):
    template_name = 'malware/upload.html'
    form_class = MalwareUploadForm
    success_url = reverse_lazy('malware.upload')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MalwareUploadView, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(
            **kwargs
        )

    def form_invalid(self, form):
        messages.info(
            self.request,
            "Your submission has not been saved. Try again."
        )
        return super(MalwareUploadView, self).form_invalid(form)

    def form_valid(self, form):
        malware = form.cleaned_data['malware']
        channels = form.cleaned_data['channels'] #list
        file_info = get_uploaded_file_info(malware)

        columns = file_info.copy()
        columns.update({
            'desc': form.cleaned_data['desc'],
            'name': form.cleaned_data['name']
        })
        # save malware into gridfs
        try:
            gridfs = connect_gridfs()
        except:
            messages.error(self.request, e)
        else:
            with gridfs.new_file() as fp:
                for chunk in malware.chunks():
                    fp.write(chunk)

                for attr, value in columns.items():
                    if attr != 'md5':
                        setattr(fp, attr, value)
                fp.close()

                # Save the owner and source of sample
                columns.update({
                    'source': form.cleaned_data['source'],
                    'user': form.user
                })
                sample = Malware(**columns)
                sample.save()
                # Save into pulishing queue 
                for c in channels:
                    Queue(malware=sample, channel=c).save()
            messages.success(self.request, 'New malware created.')
        return super(MalwareUploadView, self).form_valid(form)


class MalwareUpdateView(UpdateView):
    template_name = 'malware/update.html'
    form_class = MalwareUpdateForm
    success_url = reverse_lazy('malware.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # only owner of malware can update information
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404
        return super(MalwareUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return Malware.objects.get(slug=self.kwargs['slug'])


class MalwareListView(ListView, FormMixin):
    model = Malware
    template_name = 'malware/list.html'
    context_object_name = 'malwares'
    form_class = MalwareFilterForm
    success_url = reverse_lazy('malware.list')
    qs = None

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MalwareListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MalwareListView, self).get_context_data(**kwargs)
        context['filter'] = MalwareFilterForm()
        return context

    def get_queryset(self):
        if self.qs is not None:
            return self.qs
        return super(MalwareListView, self).get_queryset()

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.qs = form.get_queryset()
        return self.get(request, *args, **kwargs) 


class MalwareDeleteView(DeleteView):
    model = Malware
    template_name = 'malware/delete.html'
    success_url = reverse_lazy('malware.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # only owner of malware can delete malware
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404
        return super(MalwareDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return Malware.objects.get(slug=self.kwargs['slug'])

    def delete(self, request, *args, **kwargs):
        delete_file('sha256', self.kwargs['slug'])
        return super(MalwareDeleteView, self).delete(request, *args, **kwargs)


class MalwareProfileView(DetailView):
    model = Malware
    template_name = 'malware/profile.html'
    context_object_name = 'malware'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(MalwareProfileView, self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return Malware.objects.get(slug=self.kwargs['slug'])


class SourceCreateView(CreateView):
    model = SampleSource
    template_name = 'source/create.html'
    form_class = SourceForm
    fields = ['name', 'link', 'descr']
    success_url = reverse_lazy('source.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SourceCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        # Save the user
        form.instance.user = self.request.user
        return super(SourceCreateView, self).form_valid(form)


class SourceUpdateView(UpdateView):
    template_name = 'source/update.html'
    form_class = SourceForm
    fields = ['name', 'link', 'descr']
    success_url = reverse_lazy('source.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # user can only update their source
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404
        return super(SourceUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return self.model.objects.get(slug=self.kwargs['slug'], user=self.request.user)


class SourceListView(ListView):
    model = SampleSource
    template_name = 'source/list.html'
    context_object_name = 'malware_sources'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(SourceListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # user can only see their source
        return self.model.objects.filter(user=self.request.user)


class SourceDeleteView(DeleteView):
    model = SampleSource
    template_name = 'source/delete.html'
    success_url = reverse_lazy('source.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # user can only delete their source
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404
        return super(SourceDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return self.model.objects.get(slug=self.kwargs['slug'], user=self.request.user)


class SourceProfileView(DetailView):
    model = SampleSource
    template_name = 'source/profile.html'
    context_object_name = 'malware_source'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # user can only see their source
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404
        return super(SourceProfileView, self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return self.model.objects.get(slug=self.kwargs['slug'], user=self.request.user)
