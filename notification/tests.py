# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy

from core.tests import CoreTestCase
from core.tests import random_string
from notification.models import Notification

class NotificationTestCase(CoreTestCase):

    def setUp(self):
        super(NotificationTestCase, self).setUp()
        self.set_target_model(Notification)
        self.create_notification()

    def create_notification(self):
        self.subject = random_string(25)
        self.message = random_string(35)
        self.notification = Notification(
            user=self.user,
            subject=self.subject,
            message=self.message
        )
        self.notification.save()

    def test_can_list(self):
        target = reverse_lazy('notification.list')
        self.set_target(target)
        self.assert_response_status_code(200)

        response = self.get_response()
        self.assert_response_objects_count(
            response,
            'object_list',
            user=self.user
        )

    def test_can_show_detail(self):
        target = reverse_lazy(
            'notification.detail',
            args=[self.notification.id]
        )
        self.set_target(target)
        self.assert_response_status_code(200)
        response = self.get_response()

        context_object = self.get_context_object(response, 'object')
        self.assertEqual(context_object.subject, self.notification.subject)
        self.assertEqual(context_object.read, True)
