# -*- coding: utf-8 -*-
import json
import base64
import binascii
import logging

from bson.json_util import dumps

from django.http import Http404
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.core.urlresolvers import reverse_lazy

from lib import hpfeeds
from models import Channel
from core.mongodb import connect_gridfs
from malware.models import Malware


logger = logging.getLogger(__name__)


class ChannelCreateView(CreateView):
    model = Channel
    template_name = 'channel/create.html'
    success_url = reverse_lazy('channel.list')
    fields = ['name', 'host', 'port', 'ident', 'secret', 'pubchans', 'subchans']


class ChannelListView(ListView):
    model = Channel
    template_name = 'channel/list.html'
    context_object_name = 'channels'


class ChannelUpdateView(UpdateView):
    model = Channel
    template_name = 'channel/update.html'
    success_url = reverse_lazy('channel.list')
    fields = ['name', 'host', 'port', 'ident', 'secret', 'pubchans', 'subchans']


class ChannelDeleteView(DeleteView):
    model = Channel
    template_name = 'channel/delete.html'
    success_url = reverse_lazy('channel.list')


def publish(request):
    response = {}
    if request.method == 'POST':
        try:
            gridfs = connect_gridfs()
        except Exception as e:
            logger.debug(e)
            response.update({'error': ''})
            return HttpResponse(json.dumps(response), content_type='application/json')

        try:
            channel_name = request.POST['channel_name']
            malware_sha256 = request.POST['malware_sha256']
            channel = Channel.objects.get(name=channel_name)
            malware = None
            for r in gridfs.find({'sha256': malware_sha256}, limit=1):
                malware = r 
        except Exception as e:
            logger.debug(e)
            response.update({'error': '0'})
            return HttpResponse(json.dumps(response), content_type='application/json')

        try:
            hpc = hpfeeds.new(channel.host, int(channel.port), channel.ident.encode(), channel.secret.encode())
        except Exception as e:
            logger.debug(e)
            response.update({'error': '1'})
            return HttpResponse(json.dumps(response), content_type='application/json')
        else:
            data = malware.read()
            hpc.publish([channel.pubchans], data)
            error_msg = hpc.wait()
            if error_msg:
                logger.debug('got error from server: {}'.format(error_msg))
                response.update({'error': '2'})
                return HttpResponse(json.dumps(response), content_type='application/json')
            else:
                response.update({'success': '200'})
                return HttpResponse(json.dumps(response), content_type='application/json')
    
    return HttpResponse(json.dumps(response), content_type='application/json')
