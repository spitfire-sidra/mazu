# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy

from models import Notification
from core.tests import *


class NotificationTestCase(CoreTestCase):

    def setUp(self):
        super(NotificationTestCase, self).setUp()
        self._create()

    def _create(self):
        self.subject = random_string(25)
        self.message = random_string(35)
        self.notification = Notification(
            user=self.user,
            subject=self.subject,
            message=self.message
        )
        self.notification.save()

    def test_can_list(self):
        response = self.client.get(reverse_lazy('notification.list'))
        self.assertEqual(response.status_code, 200)

        count = Notification.objects.filter(user=self.user).count()
        self.assertEqual(len(response.context['object_list']), count)

    def test_can_show_detail(self):
        self._create()
        url = reverse_lazy('notification.detail', args=[self.notification.id])
        response = self.client.get(url)
        self.assertEqual(response.context['object'].subject, self.notification.subject)
        self.assertEqual(response.context['object'].read, True)
