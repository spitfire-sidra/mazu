# -*- utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse_lazy
from django.test import TestCase
from django.test import Client
from django.test import RequestFactory

from views import auth


class AuthTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.username = 'jacob'
        self.password = 'jacob_top_secret'
        self._create_user()
        self._generate_post_data()

    def _generate_post_data(self):
        self.post_data = {
            'username': self.username,
            'password': self.password
        }

    def _create_user(self):
        self.user = User.objects.create_user(
                username=self.username,
                email='jacob@example',
                password=self.password
        )

    def test_authenticate(self):
        auth = reverse_lazy('auth.views.auth')
        response = self.client.post(auth, self.post_data, follow=True)
        self.assertIsInstance(response.context['user'], User)

    def test_invalid_user(self):
        auth = reverse_lazy('auth.views.auth')
        self.post_data['password'] = 'wrong_password'
        response = self.client.post(auth, self.post_data, follow=True)
        self.assertIsInstance(response.context['user'], AnonymousUser)
