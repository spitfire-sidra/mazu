# -*- coding: utf-8 -*-
from django import forms

from models import Channel
from samples.models import SampleSource


class ChannelForm(forms.ModelForm):

    """
    Form class used for creating, updating a channel.
    """

    class Meta:
        model = Channel
        fields = [
            'default', 'name', 'host', 'port', 'identity',
            'secret', 'pubchans', 'subchans', 'source'
        ]

    def __init__(self, *args, **kwargs):
        # get current user
        self.user = kwargs.pop('user')
        super(ChannelForm, self).__init__(*args, **kwargs)
        # add a filed
        # only offers sources owned by the user
        self.fields['source'] = self.source_field()

    def source_field(self):
        return forms.ModelChoiceField(
            queryset=SampleSource.objects.filter(user=self.user),
            label='Sample Source',
            required=False
        )
