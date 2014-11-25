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


def index(request):
    context = dict()
    if request.user.is_authenticated():
        return redirect(reverse_lazy('malware.list'))
    return render_to_response(
        'registration/login.html',
        context,
        context_instance=RequestContext(request)
    )


def auth(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse_lazy('malware.list'))
        else:
            messages.error(request, 'invalid login')
    return redirect(reverse_lazy('authentication.views.index'))


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('authentication.views.index'))
    else:
        form = UserCreationForm()
    return render_to_response(
        "registration/register.html",
        {
            'form': form,
        },
        context_instance=RequestContext(request)
    )


class PasswordChangeView(FormView):
    form_class = PasswordChangeForm
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('user.passwd')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(PasswordChangeView, self).dispatch(*args, **kwargs)

    def get_form(self, form_class):
        kwargs = self.get_form_kwargs()
        kwargs['user'] = self.request.user
        return form_class(
            **kwargs
        )

    def form_valid(self, form):
        messages.success(self.request, 'Password Changed!')
        form.save()
        return super(PasswordChangeView, self).form_valid(form)


passwd = PasswordChangeView.as_view()
