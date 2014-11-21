# -*- coding: utf-8 -*-
from datetime import date
from django import forms
from django.contrib.auth.models import User
from models import SampleSource
from models import Malware
from utils import compute_hashes
from channel.models import Channel
from channel.models import Queue


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
        qs = Malware.objects.all()
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


class MalwareUploadForm(forms.Form):
    malware = forms.FileField(
        label='Malware'
    )
    name = forms.CharField(
        label='Name',
        required=False
    )
    desc = forms.CharField(
        widget=forms.Textarea,
        label='Description',
        required=False
    )
    publish = forms.BooleanField(
        label='Do you want publish?',
        required=False,
        help_text='Yes',
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(MalwareUploadForm, self).__init__(*args, **kwargs)
        self.fields['source'] = forms.ModelChoiceField(
            queryset=self.get_source_choices(self.user),
            label='Source',
            required=False
        )
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

    def get_source_choices(self, user):
        # can only mark to user's source
        return SampleSource.objects.filter(user=user)

    def clean_malware(self):
        data = self.cleaned_data['malware']
        hashes = compute_hashes(data.read())
        if Malware.objects.filter(sha256=hashes['sha256']).count() > 0:
            raise forms.ValidationError('Duplicated Malware Sample.')
        data.seek(0)
        return data

    def clean(self):
        cleaned_data = super(MalwareUploadForm, self).clean()
        publish = cleaned_data['publish']
        channels = cleaned_data['channels']

        if publish:
            if len(channels) == 0:
                raise forms.ValidationError('Please select a channel at least.')
        else:
            cleaned_data['channels'] = []
        return cleaned_data


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
        malware = Malware.objects.get(sha256=self.cleaned_data['malware'])
        for c in self.cleaned_data['channels']:
            Queue(malware=malware, channel=c).save()


class MalwareUpdateForm(forms.ModelForm):
    class Meta:
        model = Malware
        fields = ['name', 'source', 'link', 'type', 'size', 'crc32', 'md5',
                  'sha1', 'sha256', 'sha512', 'ssdeep', 'desc']
        labels = {
            'name': 'Name',
            'source': 'Source',
            'link': 'Link',
            'type': 'File Type',
            'size': 'File Size',
            'crc32': 'CRC32',
            'md5': 'MD5',
            'sha1': 'SHA1',
            'sha256': 'SHA256',
            'sha512': 'SHA512',
            'ssdeep': 'SSDEEP',
            'desc': 'Description'
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