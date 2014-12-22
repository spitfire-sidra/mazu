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
        # users can see sample sources that owned by them
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
        # Saving the user who create the sample source
        form.instance.user = self.request.user
        return super(SourceCreateView, self).form_valid(form)


class SourceUpdateView(UpdateView, OwnerRequiredMixin):

    """
    UpdateView for Source.
    Users can a source which owned by them.
    """

    model = Source
    fields = ['name', 'link', 'descr']
    form_class = SourceForm
    template_name = 'source/update.html'

    def get_success_url(self):
        source = self.get_object()
        return reverse_lazy('source.detail',  kwargs={'pk': source.pk})


class SourceDeleteView(DeleteView, OwnerRequiredMixin):

    """
    DeleteView for Source
    """

    model = Source
    template_name = 'source/delete.html'
    success_url = reverse_lazy('source.list')


class SourceDetailView(DetailView, LoginRequiredMixin):

    """
    DetailView for Source
    """

    model = Source
    template_name = 'source/detail.html'


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
        return context


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


class SampleUpdateView(DetailView, LoginRequiredMixin):

    model = Sample
    template_name = 'sample/update.html'

    def get_object(self, **kwargs):
        return self.model.objects.get(sha256=self.kwargs['sha256'])


class FilenameRemoveView(FormView, OwnerRequiredMixin):

    template_name = 'sample/remove.html'
    form_class = FilenameRemoveForm
    success_url = reverse_lazy('sample.list')

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

    def form_valid(self, form):
        form.remove_filename(self.request.user)
        return super(FilenameRemoveView, self).form_valid(form)


class FilenameAppendView(FormView, OwnerRequiredMixin):

    template_name = 'sample/append_filename.html'
    form_class = FilenameAppendForm
    success_url = reverse_lazy('sample.list')

    def get_initial(self):
        initial = super(FilenameAppendView, self).get_initial()
        try:
            sample = Sample.objects.get(sha256=self.kwargs['sha256'])
        except Sample.DoesNotExist:
            raise Http404
        else:
            initial['sample'] = sample.sha256
        return initial

    def form_valid(self, form):
        form.append_filename(self.request.user)
        return super(FilenameAppendView, self).form_valid(form)



class FilenameDeleteView(DeleteView, OwnerRequiredMixin):

    """
    A class-based view for deleting a filename.
    Only the owner can delete the filename.
    """

    model = Filename
    template_name = 'sample/delete.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self, **kwargs):
        return self.model.objects.get(id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        return super(FilenameDeleteView, self).delete(request, *args, **kwargs)


class DescriptionDeleteView(DeleteView, OwnerRequiredMixin):

    """
    A class-based view for deleting a description.
    Only the owner can delete the description.
    """

    model = Description
    template_name = 'sample/delete.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self, **kwargs):
        return self.model.objects.get(id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        return super(DescriptionDeleteView, self).delete(request, *args, **kwargs)


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
DescriptionDelete = DescriptionDeleteView.as_view()
