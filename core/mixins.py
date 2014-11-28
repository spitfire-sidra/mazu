# -*- coding: utf-8 -*-
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):

    """
    Ensures that user must be authenticated in order to access view.
    https://djangosnippets.org/snippets/2442/
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class OwnerRequiredMixin(object):

    """
    Ensures that user must be the owner of the model object.
    If not, raise HttpResponseForbidden exception.
    """

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise HttpResponseForbidden
        return super(OwnerRequiredMixin, self).dispatch(*args, **kwargs)
