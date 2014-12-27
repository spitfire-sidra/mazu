# -*- cofing: utf-8 -*-
import random

from django.core.urlresolvers import reverse_lazy

from extensions.hpfeeds.models import HPFeedsChannel
from core.tests import CoreTestCase
from core.tests import random_string


class HPFeedsChannelTestCase(CoreTestCase):

    def setUp(self):
        super(HPFeedsChannelTestCase, self).setUp()
        self.set_target_model(HPFeedsChannel)
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
        self.set_target(reverse_lazy('channel.list'))
        self.assert_response_status_code(200)
        response = self.get_response()
        self.assert_response_objects_count(
            response,
            'object_list',
            user=self.user
        )

    def test_can_create(self):
        expected = HPFeedsChannel.objects.all().count() + 1
        self.make_post_data()
        self.client.post(reverse_lazy('channel.create'), self.channel)
        count = HPFeedsChannel.objects.all().count()
        self.assertEqual(count, expected)

    def test_can_update(self):
        object_id = HPFeedsChannel.objects.get(
            name=self.channel['name'],
            user=self.user
        ).id
        self.make_post_data()
        self.client.post(
            reverse_lazy('channel.update', args=[object_id]),
            self.channel
        )
        updated = HPFeedsChannel.objects.get(id=object_id)
        self.assertEqual(updated.name, self.channel['name'])

    def test_can_delete(self):
        object_id = HPFeedsChannel.objects.get(
            name=self.channel['name'],
            user=self.user
        ).id
        expected = HPFeedsChannel.objects.all().count() - 1
        self.client.post(reverse_lazy('channel.delete', args=[object_id]))
        count = HPFeedsChannel.objects.all().count()
        self.assertEqual(count, expected)
