# -*- cofing: utf-8 -*-
import random

from django.core.urlresolvers import reverse_lazy

from sharing.models import HPFeedsChannel
from core.tests import CoreTestCase
from core.tests import random_string


class HPFeedsChannelTestCase(CoreTestCase):

    def setUp(self):
        super(HPFeedsChannelTestCase, self).setUp()
        self.create_fake_channel()

    def make_post_data(self):
        self.channel = {
            'default': True,
            'name': random_string(),
            'host': random_string(),
            'port': random.randint(1024, 65535),
            'identity': random_string(),
            'secret': random_string(),
            'pubchans': random_string(),
            'subchans': random_string(),
            'user': self.user
        }

    def create_fake_channel(self):
        self.make_post_data()
        HPFeedsChannel(**self.channel).save()

    def test_list_view(self):
        response = self.client.get(reverse_lazy('channel.list'))
        channels = HPFeedsChannel.objects.all()
        for c in response.context['object_list']:
            self.assertIn(c, channels)

    def test_display_own_channels(self):
        response = self.client.get(reverse_lazy('channel.list'))
        count = HPFeedsChannel.objects.filter(user=self.user).count()
        self.assertEqual(count, len(response.context['object_list']))

    def test_can_create(self):
        self.make_post_data()
        expected_count = HPFeedsChannel.objects.all().count() + 1
        self.client.post(reverse_lazy('channel.create'), self.channel)
        count = HPFeedsChannel.objects.all().count()
        self.assertEqual(count, expected_count)

    def test_can_update(self):
        pk = HPFeedsChannel.objects.get(name=self.channel['name'], user=self.user).id
        self.make_post_data()
        self.client.post(reverse_lazy('channel.update', args=[pk]), self.channel)
        updated_channel = HPFeedsChannel.objects.get(id=pk)
        self.assertEqual(updated_channel.name, self.channel['name'])

    def test_can_delete(self):
        expected_count = HPFeedsChannel.objects.all().count() - 1
        pk = HPFeedsChannel.objects.get(name=self.channel['name'], user=self.user).id
        self.client.post(reverse_lazy('channel.delete', args=[pk]))
        count = HPFeedsChannel.objects.all().count()
        self.assertEqual(count, expected_count)
