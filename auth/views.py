# -*- coding: utf-8 -*-
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.template import RequestContext


def index(request):
    context = dict()
    if request.user.is_authenticated():
       return redirect(reverse_lazy())
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
                return redirect(reverse_lazy('malware_list'))
        else:
            messages.error(request, 'invalid login')
    return redirect(reverse_lazy('auth.views.index'))
