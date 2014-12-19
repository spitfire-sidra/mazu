# -*- coding: utf-8 -*-
from datetime import date

from django import forms
from django.db import OperationalError
from django.forms import ValidationError
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from crispy_forms.layout import Field
from crispy_forms.layout import ButtonHolder
from crispy_forms.layout import Submit

from core.utils import compute_hashes

from samples.models import Hyperlink
from samples.models import Filename
from samples.models import Description
from samples.models import Sample
from samples.models import Source
from samples.utils import SampleHelper


class SourceForm(forms.ModelForm):

    """
    SourceForm is a form class for updating and creating Source.
    """

    class Meta:
        model = Source
        fields = ['name', 'link', 'descr']
        labels = {
            'name': 'Source Name',
            'descr': 'Description'
        }
        widgets = {
            'name': forms.TextInput(),
            'descr': forms.Textarea()
        }


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


class FilenameForm(forms.ModelForm):

    """
    A form class for saving filenames
    """

    class Meta:
        model = Filename
        fields = ['name']
        labels = {
            'name': 'Filename'
        }

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
