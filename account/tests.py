# -*- utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse_lazy
from django.test import TestCase
from django.test import Client
from django.test import RequestFactory

from account.views import auth
from core.tests import random_string


class AuthTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.make_post_data()
        self.create_fake_user()

    def make_post_data(self):
        self.username = 'jacob'
        self.password = random_string(10)
        self.post_data = {
            'username': self.username,
            'password': self.password
        }

    def create_fake_user(self):
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            email='jacob@example'
        )

    def test_authenticate(self):
        target = reverse_lazy('account.views.auth')
        response = self.client.post(target, self.post_data, follow=True)
        self.assertIsInstance(response.context['user'], User)

    def test_invalid_user(self):
        target = reverse_lazy('account.views.auth')
        self.post_data['password'] = 'wrong_password'
        response = self.client.post(target, self.post_data, follow=True)
        self.assertIsInstance(response.context['user'], AnonymousUser)
