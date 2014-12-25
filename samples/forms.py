# -*- coding: utf-8 -*-
from datetime import date

from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import ButtonHolder

from core.utils import compute_hashes

from samples.models import Hyperlink
from samples.models import Filename
from samples.models import Description
from samples.models import Sample
from samples.models import Source
from samples.utils import SampleHelper


class SampleBaseForm(forms.Form):

    """
    SampleRequiredForm contains a CharField which has widget 'HiddenInput'.
    The CharField stores a sha256 value for indicating which sample will be
    affected.
    """

    sample = forms.CharField(widget=forms.HiddenInput)

    def get_sample(self):
        """
        Trying to get the Sample by the sha256 value.

        Returns:
            None - not found
            An instance of Sample - success
        """
        sha256 = self.cleaned_data['sample']
        try:
            sample = Sample.objects.get(sha256=sha256)
        except Sample.DoesNotExist:
            return None
        else:
            return sample
        return None


class UserRequiredBaseForm(forms.Form):

    """
    UserRequiredBaseForm overwrites the __init__(*args, **kwargs) method of
    'forms.Form'. If any form class extends this Mixin, then you must overwrite
    the get_form_kwargs() method in yours CBV(Class-based View). The method
    must return a dict that contains 'User' instance with key 'user'.
    """

    def __init__(self, user, *args, **kwargs):
        super(UserRequiredBaseForm, self).__init__(*args, **kwargs)
        self.user = user


class SourceForm(forms.ModelForm):

    """
    SourceForm is a form class for updating and creating a Source.
    """

    class Meta:
        model = Source
        fields = ['name', 'link', 'descr']
        labels = {'name': 'Source Name', 'descr': 'Description'}
        widgets = {'name': forms.TextInput(), 'descr': forms.Textarea()}


class SourceAppendForm(SampleBaseForm, UserRequiredBaseForm):

    """
    A form class for appending a Source to 'Sample.sources'.
    """

    def __init__(self, user, *args, **kwargs):
        # setup self.user
        super(SourceAppendForm, self).__init__(user, *args, **kwargs)
        # add a field for Source
        self.fields['source'] = self.make_source_field()

    def make_source_field(self):
        """
        Making a ModelChoiceField for Source.
        """
        return forms.ModelChoiceField(
            queryset=Source.objects.filter(user=self.user)
        )

    def append(self):
        """
        Appending a source instance to 'Sample.sources'.

        Returns:
            An instance of 'Sample' - success
            False - failed
        """
        source = self.cleaned_data['source']
        sample = self.get_sample()

        if SampleHelper.append_source(sample, source):
            return sample

        return False


class SourceRemoveForm(SampleBaseForm, UserRequiredBaseForm):

    """
    A form class for removing a source from 'Sample.sources'.
    """

    source = forms.CharField(widget=forms.HiddenInput)

    def clean_source(self):
        """
        Validating the source field.
        Only the owner of 'source' can remove the source.

        Returns:
            An instance of Source - valid

        Raises:
            ValidationError - invalid
        """
        data = self.cleaned_data['source']
        try:
            source = Source.objects.get(id=data)
        except Source.DoesNotExist:
            raise ValidationError(_('Invalid value'))
        else:
            if source.user != self.user:
                raise ValidationError(_('Permission denied'))
            return source

    def remove(self):
        """
        Removing a source from 'Sample.sources'.
        """
        sample = self.get_sample()
        # an instance of Source
        source = self.cleaned_data['source']

        if sample and source:
            SampleHelper.remove_source(sample, source)
            return sample

        return False


class HyperlinkForm(forms.ModelForm):

    """
    A form class for saving links
    """

    class Meta:
        model = Hyperlink
        fields = ['headline', 'link', 'kind']
        widgets = {
            'link': forms.URLInput()
        }


class FilenameRemoveForm(forms.Form):

    """
    A form class for removing filenames
    """

    filename = forms.CharField(widget=forms.HiddenInput)
    sample = forms.CharField(widget=forms.HiddenInput)

    def remove_filename(self, user):
        sha256 = self.cleaned_data['sample']
        filename_id = self.cleaned_data['filename']
        try:
            sample = Sample.objects.get(sha256=sha256)
            filename = Filename.objects.get(id=filename_id)
        except Sample.DoesNotExist:
            raise Http404
        except Filename.DoesNotExist:
            raise Http404
        else:
            SampleHelper.pop_filename(sample, filename, user)


class FilenameAppendForm(forms.Form):

    """
    A form class for saving filenames
    """

    filename = forms.CharField()
    sample = forms.CharField(widget=forms.HiddenInput)

    def append_filename(self, user):
        sha256 = self.cleaned_data['sample']
        filename = self.cleaned_data['filename']
        try:
            sample = Sample.objects.get(sha256=sha256)
            filename, _ = Filename.objects.get_or_create(
                name=filename,
                user=user
            )
        except Sample.DoesNotExist:
            raise Http404
        else:
            SampleHelper.append_filename(sample, filename, user)
            return sample


class DescriptionForm(forms.ModelForm):

    """
    This class saves descriptions.
    """

    class Meta:
        model = Description
        fields = ['text']
        labels = {
            'text': 'Description'
        }


class SampleUploadForm(forms.Form):

    """
    A form for uploading sample.
    """

    filename = forms.CharField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    sample = forms.FileField()
    share = forms.BooleanField(required=False, help_text='Yes')

    def __init__(self, user, *args, **kwargs):
        super(SampleUploadForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['source'] = self.source_field(self.user)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('sample'),
            Field('share'),
            Field('source'),
            Field('filename'),
            Field('description'),
            ButtonHolder(
                Submit('submit', 'submit')
            )
        )

    def source_field(self, user):
        queryset = Source.objects.filter(user=user)
        params = {
            'required': False,
            'queryset': queryset,
            'label': 'Source'
        }
        return forms.ModelChoiceField(**params)

    def clean_sample(self):
        """
        Cleaning the sample field. If a sample already exists in database,
        then ValidationError will be raised.
        """
        sample = self.cleaned_data['sample']
        pos = sample.tell()
        hashes = compute_hashes(sample.read())
        if SampleHelper.sample_exists(sha256=hashes.sha256):
            raise ValidationError('Duplicated sample.')
        else:
            sample.seek(pos)
            return sample

    def save(self):
        """
        Saving a sample and its attributes.
        """
        filename = self.cleaned_data['filename']
        descr = self.cleaned_data['description']
        sample = self.cleaned_data['sample']
        sample_helper = SampleHelper(sample)
        saved_sample = sample_helper.save(user=self.user)
        if not saved_sample:
            return False
        sample_helper.append_filename(saved_sample, filename, self.user)
        sample_helper.save_description(saved_sample, descr, self.user)
        return True


class SampleFilterForm(forms.Form):

    """
    SampleFilterForm can filter samples. User can apply multiple filters
    in the same time.
    """

    user = forms.ModelChoiceField(
        required=False,
        label='Username',
        queryset=User.objects.filter(is_active=True)
    )
    filetype = forms.CharField(required=False, label='File Type')
    start = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'placeholder': date.today().strftime("%Y-%m-%d")}
        )
    )
    end = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={'placeholder': date.today().strftime("%Y-%m-%d")}
        )
    )

    def clean(self):
        cleaned_data = super(SampleFilterForm, self).clean()
        return cleaned_data

    def get_queryset(self):
        samples = Sample.objects.all()
        if self.cleaned_data['start']:
            samples = samples.filter(created__gte=self.cleaned_data['start'])

        if self.cleaned_data['end']:
            samples = samples.filter(created__lte=self.cleaned_data['end'])

        if self.cleaned_data['user']:
            samples = samples.filter(user=self.cleaned_data['user'])

        if self.cleaned_data['filetype']:
            samples = samples.filter(
                filetypes__filetype__icontains=self.cleaned_data['filetype']
            )
        return samples
