# -*- coding: utf-8 -*-
import os
import logging

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from models import Sample
from models import SampleSource
from models import DownloadLog
from forms import SampleUploadForm
from forms import SamplePublishForm
from forms import SampleUpdateForm
from forms import SampleFilterForm
from forms import SampleSourceForm
from core.mixins import LoginRequiredMixin
from core.mongodb import get_compressed_file
from samples.utils import delete_sample


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


class SamplePublishView(FormView, LoginRequiredMixin):

    """
    A class-based view for publishing sample.
    """

    template_name = 'malware/publish.html'
    form_class = SamplePublishForm
    success_url = reverse_lazy('malware.list')

    def get_initial(self):
        """
        Initial value of self.form_class
        """
        try:
            sha256 = self.kwargs['slug']
        except KeyError:
            raise Http404
        else:
            return {'sample': sha256}

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(**kwargs)

    def form_valid(self, form):
        form.save()
        return super(SamplePublishView, self).form_valid(form)


class SampleUploadView(FormView, LoginRequiredMixin):

    """
    Sample upload view.
    """

    template_name = 'malware/upload.html'
    form_class = SampleUploadForm
    success_url = reverse_lazy('malware.upload')

    def get_form(self, form_class):
        """
        Get current user instance, and initialize the form class.
        """
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(**kwargs)

    def form_invalid(self, form):
        messages.info(
            self.request,
            "Your submission has not been saved. Try again."
        )
        return super(SampleUploadView, self).form_invalid(form)

    def form_valid(self, form):
        if form.save_sample():
            messages.info(self.request, 'Success!')
        else:
            messages.warning(self.request, 'Can not save sample!')
        return super(SampleUploadView, self).form_valid(form)


class SampleUpdateView(UpdateView):

    """
    A class-based view for updating sample attributes.
    """

    model = Sample
    template_name = 'malware/update.html'
    form_class = SampleUpdateForm
    success_url = reverse_lazy('malware.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # only the owner of sample can update sample attributes
        sample = self.get_object()
        if sample.user != self.request.user:
            raise HttpResponseForbidden
        return super(SampleUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return self.model.objects.get(slug=self.kwargs['slug'])


class SampleListView(ListView, FormMixin, LoginRequiredMixin):

    """
    A ListView that displays samples and a filter form. This class also
    handles the POST request of filter form.
    """

    model = Sample
    template_name = 'malware/list.html'
    context_object_name = 'malwares'
    form_class = SampleFilterForm
    success_url = reverse_lazy('malware.list')
    filtered_queryset = None

    def get_context_data(self, **kwargs):
        context = super(SampleListView, self).get_context_data(**kwargs)
        context['filter'] = SampleFilterForm()
        return context

    def get_queryset(self):
        if self.filtered_queryset is not None:
            return self.filtered_queryset
        return super(SampleListView, self).get_queryset()

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.filtered_queryset = form.get_queryset()
        return self.get(request, *args, **kwargs)


class SampleDeleteView(DeleteView):

    """
    A class-based view for deleting a sample.
    """

    model = Sample
    template_name = 'malware/delete.html'
    success_url = reverse_lazy('malware.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # only the owner of scan can delete
        sample = self.get_object()
        if sample.user != self.request.user:
            raise HttpResponseForbidden
        return super(SampleDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return self.model.objects.get(slug=self.kwargs['slug'])

    def delete(self, request, *args, **kwargs):
        # delete the sample which existing in GridFS
        delete_sample(self.kwargs['slug'])
        return super(SampleDeleteView, self).delete(request, *args, **kwargs)


class SampleDetailView(DetailView, LoginRequiredMixin):

    """
    Detail view of Sample
    """

    model = Sample
    template_name = 'malware/profile.html'
    context_object_name = 'malware'

    def get_object(self, **kwargs):
        return self.model.objects.get(slug=self.kwargs['slug'])


class SampleSourceCreateView(CreateView, LoginRequiredMixin):

    """
    A class-based view for creating sample source.
    """

    model = SampleSource
    fields = ['name', 'link', 'descr']
    form_class = SampleSourceForm
    template_name = 'source/create.html'
    success_url = reverse_lazy('source.list')

    def form_valid(self, form):
        # Saving the user who create the sample source
        form.instance.user = self.request.user
        return super(SampleSourceCreateView, self).form_valid(form)


class SampleSourceUpdateView(UpdateView):

    """
    UpdateView for SampleSource
    """

    model = SampleSource
    fields = ['name', 'link', 'descr']
    form_class = SampleSourceForm
    template_name = 'source/update.html'
    success_url = reverse_lazy('source.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        # users can a source which owned by them
        source = self.get_object()
        if source.user != self.request.user:
            raise HttpResponseForbidden
        return super(SampleSourceUpdateView, self).dispatch(*args, **kwargs)

    def get_object(self):
        return self.model.objects.get(
            slug=self.kwargs['slug'],
            user=self.request.user
        )


class SampleSourceListView(ListView, LoginRequiredMixin):

    """
    ListView for SampleSource
    """

    model = SampleSource
    template_name = 'source/list.html'
    context_object_name = 'malware_sources'

    def get_queryset(self):
        # users can see sample sources that owned by them
        return self.model.objects.filter(user=self.request.user)


class SampleSourceDeleteView(DeleteView):

    """
    DeleteView for SampleSource
    """

    model = SampleSource
    template_name = 'source/delete.html'
    success_url = reverse_lazy('source.list')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        source = self.get_object()
        if source.user != self.request.user:
            raise HttpResponseForbidden
        return super(SampleSourceDeleteView, self).dispatch(*args, **kwargs)

    def get_object(self, **kwargs):
        return self.model.objects.get(
            slug=self.kwargs['slug'],
            user=self.request.user
    )


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
