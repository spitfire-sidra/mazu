# -*- coding: utf-8 -*-
from datetime import date

from django import forms
from django.db import OperationalError
from django.forms import ValidationError
from django.forms.formsets import formset_factory
from django.contrib.auth.models import User

from core.utils import compute_hashes

from samples.models import Link
from samples.models import Filename
from samples.models import Description
from samples.models import Sample
from samples.models import SampleSource
from samples.utils import sample_exists
from samples.utils import SampleHelper


class SampleSourceForm(forms.ModelForm):

    """
    SampleSourceForm is a form class for updating and creating SampleSource.
    """

    class Meta:
        model = SampleSource
        fields = ['name', 'link', 'descr']
        labels = {
            'name': 'Source Name',
            'descr': 'Description'
        }
        widgets = {
            'name': forms.TextInput(),
            'descr': forms.Textarea()
        }


class LinkForm(forms.ModelForm):

    """
    A form class for saving links
    """

    class Meta:
        model = Link
        fields = ['heading', 'url', 'kind']
        widgets = {
            'url': forms.URLInput()
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

    sample = forms.FileField()
    share = forms.BooleanField(required=False, help_text='Yes')

    def __init__(self, user, *args, **kwargs):
        super(SampleUploadForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_sample(self):
        """
        Cleaning the sample field. If a sample already exists in database,
        then ValidationError will be raised.
        """
        sample = self.cleaned_data['sample']
        pos = sample.tell()
        hashes = compute_hashes(sample.read())
        if sample_exists(sha256=hashes.sha256):
            raise ValidationError('Duplicated sample.')
        else:
            sample.seek(pos)
            return sample

    def save(self):
        """
        Saving a sample and its attributes.
        """
        sample = self.cleaned_data['sample']
        sample_helper = SampleHelper(sample)
        if sample_helper.save(user=self.user):
            return True
        return False


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
                filetype__icontains=self.cleaned_data['filetype']
            )

        return samples


class SampleUpdateForm(forms.ModelForm):

    """
    Form class for updating sample
    """

    class Meta:
        model = Sample
        fields = [
            'filetypes', 'size', 'crc32', 'md5',
            'sha1', 'sha256', 'sha512', 'ssdeep'
        ]
        labels = {
            'filetypes': 'File Type',
            'size': 'File Size',
            'crc32': 'CRC32',
            'md5': 'MD5',
            'sha1': 'SHA1',
            'sha256': 'SHA256',
            'sha512': 'SHA512',
            'ssdeep': 'ssdeep',
        }


# Formsets
FilenameFormSet = formset_factory(FilenameForm)
LinkFormSet = formset_factory(LinkForm)
