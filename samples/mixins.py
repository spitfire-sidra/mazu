# -*- coding: utf-8 -*-
from django.views.generic.edit import FormMixin

from samples.models import Sample


class SampleInitialFormMixin(FormMixin):

    """
    A FormMixin for getting the initial value for sample required forms.
    """

    def get_initial(self):
        """
        Returning a dict that would be initial values for the form_class.
        """
        initial = super(SampleInitialFormMixin, self).get_initial()
        try:
            sample = Sample.objects.get(sha256=self.kwargs['sha256'])
        except Sample.DoesNotExist:
            raise Http404
        else:
            initial['sample'] = sample.sha256
        return initial
