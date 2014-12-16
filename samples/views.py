# -*- coding: utf-8 -*-
import logging

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.contrib import messages

from core.mixins import OwnerRequiredMixin
from core.mixins import LoginRequiredMixin
from core.mongodb import get_compressed_file
from samples.utils import SampleHelper
from samples.models import Sample
from samples.models import SampleSource
from samples.models import AccessLog
from samples.forms import SampleUploadForm
from samples.forms import SampleUpdateForm
from samples.forms import SampleFilterForm
from samples.forms import SampleSourceForm
from samples.forms import DescriptionForm
from samples.forms import FilenameFormSet
from samples.forms import LinkFormSet


logger = logging.getLogger(__name__)


def download(request, sha256):
    """
    A function-based view for downloading sample
    """
    try:
        sample = get_compressed_file('sha256', sha256)
    except Exception as e:
        logger.debug(e)
        messages.error(request, 'Oops! We got an error!')
        return render(request, 'error.html')
    else:
        if sample:
            response_body = 'attachment; filename={}.zip'.format(sha256)
            response = HttpResponse(sample.read())
            response['Content-Type'] = 'application/x-zip'
            response['Content-Disposition'] = response_body
            AccessLog(user=request.user, sample=sample).save()
            return response
        else:
            raise Http404


class SampleSourceListView(ListView, LoginRequiredMixin):

    """
    ListView for SampleSource
    """

    model = SampleSource
    template_name = 'sample_source/list.html'

    def get_queryset(self):
        # users can see sample sources that owned by them
        return self.model.objects.filter(user=self.request.user)


class SampleSourceCreateView(CreateView, LoginRequiredMixin):

    """
    A class-based view for creating sample source.
    """

    model = SampleSource
    fields = ['name', 'link', 'descr']
    form_class = SampleSourceForm
    template_name = 'sample_source/create.html'
    success_url = reverse_lazy('source.list')

    def form_valid(self, form):
        # Saving the user who create the sample source
        form.instance.user = self.request.user
        return super(SampleSourceCreateView, self).form_valid(form)


class SampleSourceUpdateView(UpdateView, OwnerRequiredMixin):

    """
    UpdateView for SampleSource.
    Users can a source which owned by them.
    """

    model = SampleSource
    fields = ['name', 'link', 'descr']
    form_class = SampleSourceForm
    template_name = 'sample_source/update.html'

    def get_success_url(self):
        source = self.get_object()
        return reverse_lazy('source.detail',  kwargs={'pk': source.pk})


class SampleSourceDeleteView(DeleteView, OwnerRequiredMixin):

    """
    DeleteView for SampleSource
    """

    model = SampleSource
    template_name = 'sample_source/delete.html'
    success_url = reverse_lazy('source.list')


class SampleSourceDetailView(DetailView, LoginRequiredMixin):

    """
    DetailView for SampleSource
    """

    model = SampleSource
    template_name = 'sample_source/detail.html'


class SampleListView(ListView, FormMixin, LoginRequiredMixin):

    """
    A ListView that displays samples and a filter form. This class also
    handles the POST request of filter form.
    """

    model = Sample
    template_name = 'sample/list.html'
    form_class = SampleFilterForm
    success_url = reverse_lazy('sample.list')
    filtered_queryset = None

    def get_form_kwargs(self):
        kwargs = super(SampleUploadView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(SampleListView, self).get_context_data(**kwargs)
        context['filter_form'] = SampleFilterForm()
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


class SampleUploadView(FormView, LoginRequiredMixin):

    """
    Sample upload view.
    """

    template_name = 'sample/upload.html'
    form_class = SampleUploadForm
    success_url = reverse_lazy('sample.upload')

    def get_form_kwargs(self):
        kwargs = super(SampleUploadView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_invalid(self, form):
        messages.info(
            self.request,
            "Your submission has not been saved. Try again."
        )
        return super(SampleUploadView, self).form_invalid(form)

    def form_valid(self, form):
        if form.save():
            messages.info(self.request, 'Success!')
        else:
            messages.warning(self.request, 'Can not save sample!')
        return super(SampleUploadView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(SampleUploadView, self).get_context_data(**kwargs)
        context['filename_formset'] = FilenameFormSet()
        context['link_formset'] = LinkFormSet()
        context['description_form'] = DescriptionForm()
        return context


class SampleUpdateView(UpdateView, OwnerRequiredMixin):

    """
    A class-based view for updating sample attributes.
    Only the user of sample can update sample attributes
    """

    model = Sample
    form_class = SampleUpdateForm
    template_name = 'sample/update.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self):
        return self.model.objects.get(sha256=self.kwargs['sha256'])


class SampleDeleteView(DeleteView, OwnerRequiredMixin):

    """
    A class-based view for deleting a sample.
    Only the owner can delete the sample.
    """

    model = Sample
    template_name = 'sample/delete.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self, **kwargs):
        return self.model.objects.get(sha256=self.kwargs['sha256'])

    def delete(self, request, *args, **kwargs):
        # delete the sample which existing in GridFS
        SampleHelper.delete_sample(self.kwargs['sha256'])
        return super(SampleDeleteView, self).delete(request, *args, **kwargs)


class SampleDetailView(DetailView, LoginRequiredMixin):

    """
    Detail view of Sample
    """

    model = Sample
    template_name = 'sample/detail.html'

    def get_object(self, **kwargs):
        return self.model.objects.get(sha256=self.kwargs['sha256'])


SampleSourceList = SampleSourceListView.as_view()
SampleSourceCreate = SampleSourceCreateView.as_view()
SampleSourceUpdate = SampleSourceUpdateView.as_view()
SampleSourceDelete = SampleSourceDeleteView.as_view()
SampleSourceDetail = SampleSourceDetailView.as_view()
SampleList = SampleListView.as_view()
SampleUpload = SampleUploadView.as_view()
SampleDetail = SampleDetailView.as_view()
SampleDelete = SampleDeleteView.as_view()
SampleUpdate = SampleUpdateView.as_view()
