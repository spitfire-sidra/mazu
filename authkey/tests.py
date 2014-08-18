# -*- cofing: utf-8 -*-
import random

from django.test import Client
from django.test import TestCase
from django.core.urlresolvers import reverse_lazy

from models import AuthKey
from core.tests import random_string


class AuthKeyTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self._random_data()

    def _random_data(self):
        self.authkey = {
            'ident': random_string(),
            'secret': random_string(),
            'pubchans': random_string(),
            'subchans': random_string()
        }

    def _create(self):
        AuthKey(**self.authkey).save()

    def test_list_view(self):
        self._create()
        response = self.client.get(reverse_lazy('authkey.list'))
        authkeys = AuthKey.objects.all()
        for c in response.context['authkeys']:
            self.assertIn(c, authkeys)

    def test_can_create(self):
        expected_count = AuthKey.objects.all().count() + 1
        self.client.post(reverse_lazy('authkey.create'), self.authkey)
        count = AuthKey.objects.all().count()
        self.assertEqual(count, expected_count)

    def test_can_update(self):
        self._create()
        pk = AuthKey.objects.get(ident=self.authkey['ident']).id
        self._random_data()
        self.client.post(reverse_lazy('authkey.update', args=[pk]), self.authkey)
        updated_authkey = AuthKey.objects.get(id=pk)
        self.assertEqual(updated_authkey.ident, self.authkey['ident'])

    def test_can_delete(self):
        self._create()
        expected_count = AuthKey.objects.all().count() - 1
        pk = AuthKey.objects.get(ident=self.authkey['ident']).id
        self.client.post(reverse_lazy('authkey.delete', args=[pk]))
        count = AuthKey.objects.all().count()
        self.assertEqual(count, expected_count)
