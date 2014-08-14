# -*- cofing: utf-8 -*-
import random

from django.test import Client
from django.test import TestCase

from django.core.urlresolvers import reverse_lazy

from core.tests import random_string

from .models import Channel


class ChannelTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self._random_data()

    def _random_data(self):
        self.channel = {
            'name': random_string(),
            'host': random_string(),
            'port': random.randint(1024, 65535),
            'ident': random_string(),
            'secret': random_string(),
            'pubchans': random_string(),
            'subchans': random_string()
        }

    def _create(self):
        Channel(**self.channel).save()

    def test_list_view(self):
        self._create()
        response = self.client.get(reverse_lazy('channel_list'))
        channels = Channel.objects.all()
        for c in response.context['channels']:
            self.assertIn(c, channels)

    def test_can_create(self):
        expected_count = Channel.objects.all().count() + 1
        self.client.post(reverse_lazy('channel_create'), self.channel)
        count = Channel.objects.all().count()
        self.assertEqual(count, expected_count)

    def test_can_update(self):
        self._create()
        pk = Channel.objects.get(name=self.channel['name']).id
        self._random_data()
        self.client.post(reverse_lazy('channel_update', args=[pk]), self.channel)
        updated_channel = Channel.objects.get(id=pk)
        self.assertEqual(updated_channel.name, self.channel['name'])

    def test_can_delete(self):
        self._create()
        expected_count = Channel.objects.all().count() - 1
        pk = Channel.objects.get(name=self.channel['name']).id
        self.client.post(reverse_lazy('channel_delete', args=[pk]))
        count = Channel.objects.all().count()
        self.assertEqual(count, expected_count)
