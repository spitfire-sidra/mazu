# -*- coding: utf-8 -*-
import logging

from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.contrib import messages

from core.mixins import OwnerRequiredMixin
from core.mixins import LoginRequiredMixin
from core.mixins import UserRequiredFormMixin

from samples.utils import SampleHelper
from samples.models import Source
from samples.models import Sample
from samples.models import Filename
from samples.models import Hyperlink
from samples.models import Description
from samples.models import AccessLog
from samples.forms import SampleUploadForm
from samples.forms import SampleFilterForm
from samples.forms import SourceForm
from samples.forms import SourceAppendForm
from samples.forms import SourceRemoveForm
from samples.forms import FilenameAppendForm
from samples.forms import FilenameRemoveForm
from samples.forms import HyperlinkAppendForm
from samples.forms import HyperlinkRemoveForm
from samples.forms import DescriptionForm
from samples.mixins import SampleInitialFormMixin


logger = logging.getLogger(__name__)


def download(request, sha256):
    """
    A function-based view for downloading a sample
    """
    try:
        sample = SampleHelper.gridfs_get_sample(sha256)
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
            # feature 'AccessLog' will be added in the future
            #AccessLog(user=request.user, sample=sample).save()
            return response
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
        messages.success(self.request, 'Source created.')
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

    def form_valid(self, form):
        messages.success(self.request, 'Source details updated.')
        return super(SourceUpdateView, self).form_valid(form)


class SourceDeleteView(DeleteView, OwnerRequiredMixin):

    """
    DeleteView for Source.
    """

    model = Source
    template_name = 'source/delete.html'
    success_url = reverse_lazy('source.list')

    def form_valid(self, form):
        messages.success(self.request, 'Source deleted.')
        return super(SourceDeleteView, self).form_valid(form)


class SourceDetailView(DetailView, LoginRequiredMixin):

    """
    DetailView for Source.
    """

    model = Source
    template_name = 'source/detail.html'


class SampleUpdateBaseView(FormView):

    """
    A base view class for updating sample.
    """

    def get_success_url(self):
        """
        If sample updated, then the view will be redirect to the following URL.
        """
        return reverse_lazy(
            'sample.update',
            kwargs={'sha256': self.sample.sha256}
        )


class SourceAppendView(SampleUpdateBaseView, UserRequiredFormMixin,\
                        SampleInitialFormMixin, OwnerRequiredMixin):

    """
    Building a relationship between a Sample and a Source.
    """

    template_name = 'sample/append_source.html'
    form_class = SourceAppendForm

    def form_valid(self, form):
        self.sample, result = form.append()
        if not result:
            messages.error(
                self.request,
                'Failed to append Source. Source already exists.'
            )
        else:
            messages.success(self.request, 'Source appended.')
        return super(SourceAppendView, self).form_valid(form)


class SourceRemoveView(SampleUpdateBaseView, UserRequiredFormMixin,\
                        SampleInitialFormMixin, OwnerRequiredMixin):

    """
    This class just breaks the relationship between a Source and a Sample.
    """

    template_name = 'sample/remove.html'
    form_class = SourceRemoveForm

    def get_object(self):
        """
        Trying to get the Source by self.kwargs['source_pk'].
        """
        try:
            source = Source.objects.get(id=self.kwargs['source_pk'])
        except Source.DoesNotExist:
            raise Http404
        else:
            return source

    def get_initial(self):
        """
        Returning a dict that would be initial values for the form_class.
        """
        initial = super(SourceRemoveView, self).get_initial()
        initial['source'] = self.get_object().pk
        return initial

    def form_valid(self, form):
        self.sample, result = form.remove()
        if not result:
            messages.error(self.request, 'Failed to remove the source.')
        else:
            messages.success(self.request, 'Source removed.')
        return super(SourceRemoveView, self).form_valid(form)


class FilenameAppendView(SampleUpdateBaseView, UserRequiredFormMixin,\
                            SampleInitialFormMixin):

    """
    Building a relationship between a Sample and a Filename.
    """

    template_name = 'sample/append_filename.html'
    form_class = FilenameAppendForm

    def form_valid(self, form):
        self.sample, result = form.append()
        if not result:
            messages.error(self.request, 'Failed to append the filename.')
        else:
            messages.success(self.request, 'Filename appended.')
        return super(FilenameAppendView, self).form_valid(form)


class FilenameRemoveView(SampleUpdateBaseView, UserRequiredFormMixin,\
                            SampleInitialFormMixin, OwnerRequiredMixin):
    """
    This class just breaks the relationship between a Filename and a Sample.
    """

    template_name = 'sample/remove.html'
    form_class = FilenameRemoveForm

    def get_object(self):
        """
        Trying to get the Filename by self.kwargs['filename_pk'].
        """
        try:
            filename = Filename.objects.get(id=self.kwargs['filename_pk'])
        except Filename.DoesNotExist:
            raise Http404
        else:
            return filename

    def get_initial(self):
        """
        Returning a dict that would be initial values for the form_class.
        """
        initial = super(FilenameRemoveView, self).get_initial()
        initial['filename'] = self.get_object().pk
        return initial

    def form_valid(self, form):
        self.sample, result = form.remove()
        if not result:
            messages.error(self.request, 'Failed to remove the filename.')
        else:
            messages.success(self.request, 'Filename appended.')
        return super(FilenameRemoveView, self).form_valid(form)


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

    def form_valid(self, form):
        messages.success(self.request, 'Filename deleted.')
        return super(FilenameDeleteView, self).form_valid(form)


class HyperlinkAppendView(SampleUpdateBaseView, UserRequiredFormMixin,\
                            SampleInitialFormMixin):

    """
    Building a relationship between a Sample and a Hyperlink.
    """

    template_name = 'sample/append_hyperlink.html'
    form_class = HyperlinkAppendForm

    def form_valid(self, form):
        self.sample, result = form.append()
        if not result:
            messages.error(self.request, 'Failed to append the Hyperlink.')
        else:
            messages.success(self.request, 'Hyperlink appended.')
        return super(HyperlinkAppendView, self).form_valid(form)


class HyperlinkRemoveView(SampleUpdateBaseView, UserRequiredFormMixin,\
                            SampleInitialFormMixin, OwnerRequiredMixin):
    """
    This class just breaks the relationship between a Filename and a Sample.
    """

    template_name = 'sample/remove.html'
    form_class = HyperlinkRemoveForm

    def get_object(self):
        """
        Trying to get the Hyperlink by self.kwargs['hyperlink_pk'].
        """
        try:
            hyperlink = Hyperlink.objects.get(id=self.kwargs['hyperlink_pk'])
        except Hyperlink.DoesNotExist:
            raise Http404
        else:
            return hyperlink

    def get_initial(self):
        """
        Returning a dict that would be initial values for the form_class.
        """
        initial = super(HyperlinkRemoveView, self).get_initial()
        initial['hyperlink'] = self.get_object().pk
        return initial

    def form_valid(self, form):
        self.sample, result = form.remove()
        if not result:
            messages.error(self.request, 'Failed to remove the hyperlink.')
        else:
            messages.success(self.request, 'Hyperlink appended.')
        return super(HyperlinkRemoveView, self).form_valid(form)


class HyperlinkDeleteView(DeleteView, OwnerRequiredMixin):

    """
    A class-based view for deleting a hyperlink.
    This CBV not only breaks the relationship between a Hyperlink and
    Samples but deletes the Hyperlink from database.
    Only the owner can delete the filename which owned by himself.
    """

    model = Hyperlink
    template_name = 'sample/delete.html'
    success_url = reverse_lazy('sample.list')

    def get_object(self, **kwargs):
        return self.model.objects.get(id=self.kwargs['pk'])

    def form_valid(self, form):
        messages.success(self.request, 'hyperlink deleted.')
        return super(HyperlinkDeleteView, self).form_valid(form)


class SampleListView(ListView, UserRequiredFormMixin, LoginRequiredMixin):

    """
    A ListView that displays samples and a filter form.
    This class also handles the POST request from the filter form.
    """

    model = Sample
    template_name = 'sample/list.html'
    form_class = SampleFilterForm
    success_url = reverse_lazy('sample.list')
    filtered_queryset = None

    def get_context_data(self, **kwargs):
        context = super(SampleListView, self).get_context_data(**kwargs)
        context['filter_form'] = SampleFilterForm()
        return context

    def get_queryset(self):
        if self.filtered_queryset is not None:
            return self.filtered_queryset
        return super(SampleListView, self).get_queryset()

    def post(self, request, *args, **kwargs):
        """
        If we got a 'request.POST', the 'self.filtered_queryset' would be the
        queryset that had been filtered.
        Then we forward the rest jobs to 'self.get(request, *args, **kwargs)'
        for displaying the web page.
        """
        form = self.form_class(request.POST)
        if form.is_valid():
            self.filtered_queryset = form.get_queryset()
        return self.get(request, *args, **kwargs)


class SampleUploadView(FormView, UserRequiredFormMixin, LoginRequiredMixin):

    """
    Class-based view for uploading sample.
    """

    template_name = 'sample/upload.html'
    form_class = SampleUploadForm
    success_url = reverse_lazy('sample.upload')

    def form_invalid(self, form):
        messages.error(
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
        SampleHelper.gridfs_delete_sample(self.kwargs['sha256'])
        return super(SampleDeleteView, self).delete(request, *args, **kwargs)


class SampleDetailView(DetailView, LoginRequiredMixin):

    """
    DetailView for Sample.
    """

    model = Sample
    template_name = 'sample/detail.html'

    def get_object(self, **kwargs):
        return self.model.objects.get(sha256=self.kwargs['sha256'])


class SampleUpdateView(SampleDetailView):

    """
    UpdateView for Sample.
    Actually, it's a DetailView but uses a different template.
    """

    template_name = 'sample/update.html'


class DescriptionCreateView(CreateView, LoginRequiredMixin,\
                            SampleUpdateBaseView):

    """
    A class-based view for creating Description.
    """

    model = Description
    fields = ['text']
    template_name = 'source/create.html'

    def get_sample(self):
        """
        Trying to get the sample by sha256.
        """
        try:
            sample = Sample.objects.get(sha256=self.kwargs['sha256'])
        except Sample.DoesNotExist:
            return False
        else:
            return sample

    def form_valid(self, form):
        # saving the user who creates the source
        form.instance.user = self.request.user

        # get the sample
        self.sample = self.get_sample()
        if not self.sample:
            raise Http404
        # saveing the sample which maps to this description
        form.instance.sample = self.sample
        messages.success(self.request, 'Description created.')
        return super(DescriptionCreateView, self).form_valid(form)


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

    def get_success_url(self):
        descr = self.get_object()
        return reverse_lazy(
            'sample.update',
            kwargs={'sha256': descr.sample.sha256}
        )


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
HyperlinkAppend = HyperlinkAppendView.as_view()
HyperlinkRemove = HyperlinkRemoveView.as_view()
HyperlinkDelete = HyperlinkDeleteView.as_view()
SourceAppend = SourceAppendView.as_view()
SourceRemove = SourceRemoveView.as_view()
DescriptionCreate = DescriptionCreateView.as_view()
DescriptionDelete = DescriptionDeleteView.as_view()
DescriptionUpdate = DescriptionUpdateView.as_view()
