# -*- coding: utf-8 -*-
from datetime import date

from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import Submit
from crispy_forms.layout import ButtonHolder

from core.utils import compute_hashes

from sharing.models import SharingList

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
        result = SampleHelper.append_source(sample, source)
        return (sample, result)


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
        result = SampleHelper.remove_source(sample, source)
        return (sample, result)


class FilenameAppendForm(SampleBaseForm, UserRequiredBaseForm):

    """
    A form class for saving filenames
    """

    filename = forms.CharField()

    def clean_filename(self):
        """
        Trying to get the filename instance.
        If there is no corresponding filename,
        then create one for the filename.
        """
        data = self.cleaned_data['filename']
        try:
            filename, created = Filename.objects.get_or_create(
                name=data,
                user=self.user
            )
        except Exception:
            raise ValidationError(_('Invalid value'))
        else:
            return filename

    def append(self):
        """
        Append a filename instance to 'sample.filenames'
        """
        sample = self.get_sample()
        filename = self.cleaned_data['filename']
        result = SampleHelper.append_filename(sample, filename)
        return (sample, result)


class FilenameRemoveForm(SampleBaseForm, UserRequiredBaseForm):

    """
    A form class for removing filenames
    """

    filename = forms.CharField(widget=forms.HiddenInput)

    def clean_filename(self):
        """
        Validating the filename field.
        Only the owner of 'filename' can remove the filename.

        Returns:
            An instance of Filename - valid

        Raises:
            ValidationError - invalid
        """
        data = self.cleaned_data['filename']
        try:
            filename = Filename.objects.get(id=data)
        except Filename.DoesNotExist:
            raise ValidationError(_('Invalid value'))
        else:
            if filename.user != self.user:
                raise ValidationError(_('Permission denied'))
            return filename

    def remove(self):
        """
        Removing the filename from 'sample.filenames'
        """
        sample = self.get_sample()
        filename = self.cleaned_data['filename']
        result = SampleHelper.remove_filename(sample, filename)
        return (sample, result)


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


# This form class is not used yet.
class HyperlinkForm(forms.ModelForm):

    """
    A form class for saving links.
    """

    class Meta:
        model = Hyperlink
        fields = ['headline', 'link', 'kind']
        widgets = {
            'link': forms.URLInput()
        }


class SampleUploadForm(UserRequiredBaseForm):

    """
    A form class for uploading sample. We are trying to keep this form simple.
    So this form only provides one filename field, one description field and
    one source field for the user who wants to upload a sample.
    """

    sample = forms.FileField()
    filename = forms.CharField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    share = forms.BooleanField(required=False, help_text='Yes')

    def __init__(self, user, *args, **kwargs):
        # setup 'self.user'.
        super(SampleUploadForm, self).__init__(user, *args, **kwargs)
        self.fields['source'] = self.make_source_field()
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

    def make_source_field(self):
        """
        Users are only allowed to choice their own source.
        """
        return forms.ModelChoiceField(
            label='Source',
            required=False,
            queryset=Source.objects.filter(user=self.user)
        )

    def clean_sample(self):
        """
        Cleaning the sample field. If a sample already exists in database,
        then ValidationError will be raised.
        """
        temp_file = self.cleaned_data['sample']
        pos = temp_file.tell()
        hashes = compute_hashes(temp_file.read())
        if SampleHelper.sample_exists(sha256=hashes.sha256):
            raise ValidationError(_('Duplicated sample.'))
        else:
            temp_file.seek(pos)
            return temp_file

    def clean_filename(self):
        """
        Trying to get the filename instance. If it is none, then creates one.

        Returns:
            an instance of Filename - valid

        Raises:
            ValidationError - invalid
        """
        data = self.cleaned_data['filename']
        try:
            filename, created = Filename.objects.get_or_create(
                name=data,
                user=self.user
            )
        except Exception as e:
            raise ValidationError(_('Invalid value.'))
        else:
            return filename

    def save(self):
        """
        Saving a sample and its attributes.
        """
        # file pointer
        sample_fp = self.cleaned_data['sample']
        # an instance of Filename
        filename = self.cleaned_data['filename']
        text = self.cleaned_data['description']
        share = self.cleaned_data['share']

        helper = SampleHelper(sample_fp)
        sample = helper.save(user=self.user)
        if not sample:
            return False

        helper.append_filename(sample, filename)
        helper.save_description(sample, text, self.user)
        # add to share list
        if share:
            SharingList(sample=sample, user=self.user).save()
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
