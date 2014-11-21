# -*- coding: utf-8 -*-
from datetime import date

from django import forms
from django.forms import ValidationError
from django.contrib.auth.models import User

from channel.models import Channel
from channel.models import Queue

from core.utils import compute_hashes
from samples.models import Sample
from samples.models import SampleSource
from samples.utils import save_sample
from samples.utils import delete_sample
from samples.utils import get_file_attrs


class MalwareFilterForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        label='User',
        required=False
    )
    type = forms.CharField(
        label='File Type',
        required=False
    )
    start = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': date.today().strftime("%Y-%m-%d")}),
        required=False
    )
    end = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': date.today().strftime("%Y-%m-%d")}),
        required=False
    )

    def clean(self):
        cleaned_data = super(MalwareFilterForm, self).clean()
        return cleaned_data

    def get_queryset(self):
        qs = Sample.objects.all()
        if self.cleaned_data['start']:
            s = self.cleaned_data['start']
            qs = qs.filter(created__gte=s)

        if self.cleaned_data['end']:
            e = self.cleaned_data['end']
            qs = qs.filter(created__lte=e)

        if self.cleaned_data['user']:
            qs = qs.filter(user=self.cleaned_data['user'])

        if self.cleaned_data['type']:
            qs = qs.filter(type__icontains=self.cleaned_data['type'])

        return qs


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
        self.fields['channels'] = self.channels_filed(self.user)

    def channels_filed(self, user):
        queryset = Channel.objects.filter(owner=user)
        # get all default channels
        initial = (r for r in queryset if r.default)
        params = {
            'required': False,
            'queryset': queryset,
            'label': 'Select channels to publish',
            'widget': forms.CheckboxSelectMultiple,
            'initial': initial
        }
        return forms.ModelMultipleChoiceField(**params)

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

    def clean(self):
        """
        Cleaning all fields in this form class. If a user choose to publish a
        sample but did not choice any channls, ValidationError would be raised.
        """
        cleaned_data = super(SampleUploadForm, self).clean()

        if cleaned_data['publish'] and len(cleaned_data['channels']) == 0:
            raise ValidationError('Please select a channel at least.')
        else:
            cleaned_data['channels'] = []
        return cleaned_data

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

    def save_publish_queue(self):
        pass


class MalwarePublishForm(forms.Form):
    malware = forms.CharField(
        widget=forms.HiddenInput,
        label='',
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MalwarePublishForm, self).__init__(*args, **kwargs)
        self.fields['channels'] = forms.ModelMultipleChoiceField(
            queryset=self.get_channels_choices(self.user),
            widget=forms.CheckboxSelectMultiple,
            label='Publish to',
            initial=self.get_channels_initial(self.user),
            required=False
        )

    def get_channels_choices(self, user):
        # can only publish to user's channel
        return Channel.objects.filter(owner=user)

    def get_channels_initial(self, user):
        channels = self.get_channels_choices(user)
        return (c for c in channels if c.default)

    def save(self):
        malware = Sample.objects.get(sha256=self.cleaned_data['malware'])
        for c in self.cleaned_data['channels']:
            Queue(malware=malware, channel=c).save()


class MalwareUpdateForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ['type', 'size', 'crc32', 'md5',
                  'sha1', 'sha256', 'sha512', 'ssdeep']
        labels = {
            'type': 'File Type',
            'size': 'File Size',
            'crc32': 'CRC32',
            'md5': 'MD5',
            'sha1': 'SHA1',
            'sha256': 'SHA256',
            'sha512': 'SHA512',
            'ssdeep': 'SSDEEP',
        }


class SourceForm(forms.ModelForm):
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
