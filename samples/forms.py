# -*- coding: utf-8 -*-
from datetime import date

from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User

from sharing.models import HPFeedsChannel
from sharing.models import HPFeedsPubQueue

from core.utils import compute_hashes
from samples.models import Sample
from samples.models import SampleSource
from samples.utils import save_sample
from samples.utils import delete_sample
from samples.utils import get_file_attrs


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


class SampleUploadForm(forms.Form):

    """
    A form for uploading sample.
    This class contains some dirty hacks in __init__(*args, **kwargs).
    """

    sample = forms.FileField()
    name = forms.CharField(required=False)
    descr = forms.CharField(
        required=False,
        label='Description',
        widget=forms.Textarea
    )
    publish = forms.BooleanField(
        required=False,
        label='Publish?',
        help_text='Yes'
    )

    def __init__(self, *args, **kwargs):
        # get user instance
        self.user = kwargs.pop('user')

        super(SampleUploadForm, self).__init__(*args, **kwargs)

        # !dirty hack!
        # Adding a form field that only list samples sources owned by an user
        self.fields['sample_source'] = self.sample_source_field(self.user)

    def sample_source_field(self, user):
        queryset = SampleSource.objects.filter(user=user)
        params = {
            'required': False,
            'queryset': queryset,
            'label': 'Sample source'
        }
        return forms.ModelChoiceField(**params)

    def clean_sample(self):
        """
        Cleaning the sample field. If a sample already exists in database,
        then ValidationError will be raised.
        """
        sample = self.cleaned_data['sample']
        hashes = compute_hashes(sample.read())
        try:
            Sample.objects.get(sha256=hashes.sha256)
        except Sample.DoesNotExist:
            # sets the file's current position at the beginning
            sample.seek(0)
            return sample
        else:
            raise ValidationError('Duplicated sample.')

    def save_sample(self):
        """
        Saving a sample and its attributes.
        """
        sample = self.cleaned_data['sample']
        attrs = get_file_attrs(sample)
        # saving who uploaded this sample
        attrs['user'] = self.user
        if save_sample(sample.read()):
            if self.save_sample_attrs(attrs):
                return True
            # if didn't save attributes into database,
            # delete the sample that saved in GridFS.
            delete_sample(attrs['sha256'])
        return False

    def save_sample_attrs(self, attrs):
        try:
            Sample(**attrs).save()
        except Exception:
            return False
        else:
            return True


class SamplePublishForm(forms.Form):

    """
    User can choice channels that a sample will be published.
    """

    sample = forms.CharField(
        required=False,
        label='',
        widget=forms.HiddenInput,
    )

    def __init__(self, *args, **kwargs):
        # get current user instance
        self.user = kwargs.pop('user')
        super(SamplePublishForm, self).__init__(*args, **kwargs)
        # add a field 'channels'
        self.fields['channels'] = self.channels_field()

    def channels_field(self):
        # user are allowed to publish samples on their own channels
        queryset = HPFeedsChannel.objects.filter(user=self.user)
        initial = (chann for chann in queryset if chann.default)
        field = forms.ModelMultipleChoiceField(
            required=False,
            queryset=queryset,
            initial=initial,
            label='Publish to',
            widget=forms.CheckboxSelectMultiple
        )

    def clean_channels(self):
        channels = self.cleaned_data['channels']
        if len(channels) == 0:
            ValidationError('Please choice at least one channel.')
        return channels

    def save(self):
        try:
            sample = Sample.objects.get(sha256=self.cleaned_data['sample'])
        except sample.DoesNotExist:
            return False
        else:
            for chann in self.cleaned_data['channels']:
                HPFeedsPubQueue(sample=sample, channel=chann).save()
            return True


class SampleUpdateForm(forms.ModelForm):

    """
    Form class for updating sample
    """

    class Meta:
        model = Sample
        fields = [
            'filetype', 'size', 'crc32', 'md5',
            'sha1', 'sha256', 'sha512', 'ssdeep'
        ]
        labels = {
            'filetype': 'File Type',
            'size': 'File Size',
            'crc32': 'CRC32',
            'md5': 'MD5',
            'sha1': 'SHA1',
            'sha256': 'SHA256',
            'sha512': 'SHA512',
            'ssdeep': 'ssdeep',
        }


class SampleSourceForm(forms.ModelForm):

    """
    SampleSourceForm is a form class for updating and creating SampleSource.
    """

    class Meta:
        model = SampleSource
        fields = ['name', 'link', 'descr']
        labels = {
            'name': 'Label',
            'descr': 'Description'
        }
        widgets = {
            'name': forms.TextInput(),
            'descr': forms.Textarea()
        }
