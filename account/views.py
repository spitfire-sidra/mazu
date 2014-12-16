# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.template import RequestContext
from django.views.generic.edit import FormView

from core.mixins import LoginRequiredMixin


def index(request):
    """
    Function-based view for displaying index
    """
    context = dict()
    if request.user.is_authenticated():
        return redirect(reverse_lazy('sample.list'))

    return render_to_response(
        'registration/login.html',
        context,
        context_instance=RequestContext(request)
    )


def auth(request):
    """
    Authentication
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect(reverse_lazy('sample.list'))
        else:
            messages.error(request, 'invalid login')

    return redirect(reverse_lazy('account.views.index'))


def signup(request):
    """
    If an user had login, then redirect to index.
    """
    if request.user.is_authenticated():
        return redirect(reverse_lazy('sample.list'))

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('account.views.index'))

    return render_to_response(
        "registration/register.html",
        {'form': UserCreationForm(),},
        context_instance=RequestContext(request)
    )


class PasswordChangeView(FormView, LoginRequiredMixin):

    """
    A class-based handles changing password.
    """

    form_class = PasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('user.passwd')

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(**kwargs)

    def form_valid(self, form):
        messages.success(self.request, 'Password Changed!')
        form.save()
        return super(PasswordChangeView, self).form_valid(form)


passwd = PasswordChangeView.as_view()
