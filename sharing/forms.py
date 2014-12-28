# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse_lazy


from settings.sharing_extensions import EXT_CHOICES


class SelectExtensionForm(forms.Form):

    choice = forms.ChoiceField(choices=EXT_CHOICES)
    sample = forms.CharField(widget=forms.HiddenInput)

    def get_redirect_url(self):
        url_name = 'sharing-via-{0}'.format(self.cleaned_data['choice'])
        return reverse_lazy(
            url_name,
            kwargs={
                'sha256': self.cleaned_data['sample']
            }
        )
