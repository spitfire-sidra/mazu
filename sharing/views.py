# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.core.urlresolvers import NoReverseMatch
from django.views.generic.edit import FormView
from django.contrib import messages

from core.mixins import LoginRequiredMixin

from sharing.forms import SelectExtensionForm


class SelectExtensionView(FormView, LoginRequiredMixin):

    """
    FormView for sharing samples.
    """

    form_class = SelectExtensionForm
    template_name = 'form.html'

    def get_initial(self):
        """
        Giving the initial value (sha256) to self.form_class.
        """
        initial = super(SelectExtensionView, self).get_initial()
        initial['sample'] = self.kwargs['sha256']
        return initial

    def get_success_url(self):
        """
        **NOTICE**
        If the redirect() is out of function, this method will be called.
        That's say this method is actually "get_failed_url()".
        """
        return reverse_lazy(
            'sharing.select.extension',
            kwargs={'sha256': self.kwargs['sha256']}
        )

    def form_valid(self, form):
        """
        If the form is valid, redirect to the following URL.
        """
        try:
            return redirect(form.get_redirect_url())
        except NoReverseMatch:
            message_fmt = "The module '{0}' is not working."
            messages.error(
                self.request,
                message_fmt.format(form.cleaned_data['choice'])
            )
            # if can't redirect
            return super(SelectExtensionView, self).form_valid(form)


# Alias
SelectExtension = SelectExtensionView.as_view()
