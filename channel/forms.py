# -*- coding: utf-8 -*-
from django import forms

from models import Channel
from samples.models import Source


class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['default', 'name', 'host', 'port', 'ident', 'secret', 'pubchans', 'subchans', 'source']


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ChannelForm, self).__init__(*args, **kwargs)
        self.fields['source'] = forms.ModelChoiceField(
            queryset=self.get_source_choices(self.user),
            label='Source',
            required=False
        )

    def get_source_choices(self, user):
        return Source.objects.filter(user=user)
