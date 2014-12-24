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
from samples.models import Filename
from samples.models import Description
from samples.models import Source
from samples.models import AccessLog
from samples.forms import SampleUploadForm
from samples.forms import SampleFilterForm
from samples.forms import SourceForm
from samples.forms import SourceAppendForm
from samples.forms import SourceRemoveForm
from samples.forms import FilenameRemoveForm
from samples.forms import FilenameAppendForm
from samples.forms import DescriptionForm


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


class SourceListView(ListView, LoginRequiredMixin):

    """
    ListView for Source
    """

    model = Source
    template_name = 'source/list.html'

    def get_queryset(self):
        # users can see sample sources that owned by themself
        return self.model.objects.filter(user=self.request.user)


class SourceCreateView(CreateView, LoginRequiredMixin):

    """
    A class-based view for creating sample source.
    """

    model = Source
    fields = ['name', 'link', 'descr']
    form_class = SourceForm
    template_name = 'source/create.html'
    success_url = reverse_lazy('source.list')

    def form_valid(self, form):
        # Saving the user who creates the source
        form.instance.user = self.request.user
        return super(SourceCreateView, self).form_valid(form)


class SourceUpdateView(UpdateView, OwnerRequiredMixin):

    """
    UpdateView for Source.
    Users can update a source which owned by himself.
    """

    model = Source
    fields = ['name', 'link', 'descr']
    form_class = SourceForm
    template_name = 'source/update.html'

    def get_success_url(self):
        source = self.get_object()
        return reverse_lazy('source.detail', kwargs={'pk': source.pk})


class SourceDeleteView(DeleteView, OwnerRequiredMixin):

    """
    DeleteView for Source.
    """

    model = Source
    template_name = 'source/delete.html'
    success_url = reverse_lazy('source.list')


class SourceDetailView(DetailView, LoginRequiredMixin):

    """
    DetailView for Source.
    """

    model = Source
    template_name = 'source/detail.html'


class SourceAppendView(FormView, OwnerRequiredMixin):

    """
    Building a relationship between a Sample and a Source.
    """

    template_name = 'sample/append_source.html'
    form_class = SourceAppendForm

    def get_initial(self):
        initial = super(SourceAppendView, self).get_initial()
        try:
            sample = Sample.objects.get(sha256=self.kwargs['sha256'])
        except Sample.DoesNotExist:
            raise Http404
        else:
            initial['sample'] = sample.sha256
        return initial

    def get_form_kwargs(self):
        kwargs = super(SourceAppendView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy(
            'sample.detail',
            kwargs={'sha256': self.sample.sha256}
        )

    def form_valid(self, form):
        self.sample = form.append_source()
        return super(SourceAppendView, self).form_valid(form)


class SourceRemoveView(FormView, OwnerRequiredMixin):

    """
    This class just breaks the relationship between a Source and a Sample.
    """

    template_name = 'sample/remove.html'
    form_class = SourceRemoveForm

    def get_initial(self):
        initial = super(SourceRemoveView, self).get_initial()
        try:
            sample = Sample.objects.get(sha256=self.kwargs['sha256'])
            source = Source.objects.get(id=self.kwargs['source_pk'])
        except Sample.DoesNotExist:
            raise Http404
        except Source.DoesNotExist:
            raise Http404
        else:
            initial['source'] = source.pk
            initial['sample'] = sample.sha256
        return initial

    def get_success_url(self):
        return reverse_lazy(
            'sample.detail',
            kwargs={'sha256': self.sample.sha256}
        )

    def form_valid(self, form):
        self.sample = form.remove_source(self.request.user)
        return super(SourceRemoveView, self).form_valid(form)


class SampleListView(ListView, FormMixin, LoginRequiredMixin):

    """
    A ListView that displays samples and a filter form.
    This class also handles the POST request from the filter form.
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
        return context


class SampleDeleteView(DeleteView, OwnerRequiredMixin):

    """
    DeleteView for Sample.
    Only the owner of the sample can delete it.
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
    DetailView for Sample.
    """

    model = Sample
    template_name = 'sample/detail.html'

    def get_object(self, **kwargs):
        return self.model.objects.get(sha256=self.kwargs['sha256'])


class SampleUpdateView(DetailView, LoginRequiredMixin):

    """
    UpdateView for Sample.
    Actually, it's a DetailView but uses a different template.
    """

    model = Sample
    template_name = 'sample/update.html'

    def get_object(self, **kwargs):
        return self.model.objects.get(sha256=self.kwargs['sha256'])


class FilenameRemoveView(FormView, OwnerRequiredMixin):

    """
    This class just breaks the relationship between a Filename and a Sample.
    """

    template_name = 'sample/remove.html'
    form_class = FilenameRemoveForm

    def get_initial(self):
        initial = super(FilenameRemoveView, self).get_initial()
        try:
            sample = Sample.objects.get(sha256=self.kwargs['sha256'])
            filename = Filename.objects.get(id=self.kwargs['filename_pk'])
        except Sample.DoesNotExist:
            raise Http404
        except Filename.DoesNotExist:
            raise Http404
        else:
            initial['filename'] = filename.pk
            initial['sample'] = sample.sha256
        return initial

    def get_success_url(self):
        return reverse_lazy(
            'sample.detail',
            kwargs={'sha256': self.sample.sha256}
        )

    def form_valid(self, form):
        self.sample = form.remove_filename(self.request.user)
        return super(FilenameRemoveView, self).form_valid(form)


class FilenameAppendView(FormView, OwnerRequiredMixin):

    """
    Building a relationship between a Sample and a Filename.
    """

    template_name = 'sample/append_filename.html'
    form_class = FilenameAppendForm

    def get_initial(self):
        initial = super(FilenameAppendView, self).get_initial()
        try:
            sample = Sample.objects.get(sha256=self.kwargs['sha256'])
        except Sample.DoesNotExist:
            raise Http404
        else:
            initial['sample'] = sample.sha256
        return initial

    def get_success_url(self):
        return reverse_lazy(
            'sample.detail',
            kwargs={'sha256': self.sample.sha256}
        )

    def form_valid(self, form):
        self.sample = form.append_filename(self.request.user)
        return super(FilenameAppendView, self).form_valid(form)


class FilenameDeleteView(DeleteView, OwnerRequiredMixin):

    """
    A class-based view for deleting a filename.
    This CBV not only breaks the relationship between a Filename and
    Samples but deletes the Filename from database.
    Only the owner can delete the filename which owned by himself.
    """

    model = Filename
    template_name = 'sample/delete.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self, **kwargs):
        return self.model.objects.get(id=self.kwargs['pk'])


class DescriptionDeleteView(DeleteView, OwnerRequiredMixin):

    """
    DeleteView for Description.
    Only the owner of the description can delete the description.
    """

    model = Description
    template_name = 'sample/delete.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self, **kwargs):
        return self.model.objects.get(id=self.kwargs['pk'])


class DescriptionUpdateView(UpdateView, OwnerRequiredMixin):

    """
    UpdateView for Description.
    Only the owner of the description can update the description.
    """

    model = Description
    fields = ['text']
    form_class = DescriptionForm
    template_name = 'sample/update_description.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self, **kwargs):
        return self.model.objects.get(id=self.kwargs['pk'])


# Alias
SourceList = SourceListView.as_view()
SourceCreate = SourceCreateView.as_view()
SourceUpdate = SourceUpdateView.as_view()
SourceDelete = SourceDeleteView.as_view()
SourceDetail = SourceDetailView.as_view()
SampleList = SampleListView.as_view()
SampleUpload = SampleUploadView.as_view()
SampleDetail = SampleDetailView.as_view()
SampleDelete = SampleDeleteView.as_view()
SampleUpdate = SampleUpdateView.as_view()
FilenameDelete = FilenameDeleteView.as_view()
FilenameRemove = FilenameRemoveView.as_view()
FilenameAppend = FilenameAppendView.as_view()
SourceAppend = SourceAppendView.as_view()
SourceRemove = SourceRemoveView.as_view()
DescriptionDelete = DescriptionDeleteView.as_view()
DescriptionUpdate = DescriptionUpdateView.as_view()
