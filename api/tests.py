# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework import status

from core.tests import random_string
from samples.tests import make_sample_file
from samples.tests import remove_temp_folder


class SampleTests(APITestCase):

    """
    Testcase for api of 'samples' app.
    """

    def setUp(self):
        user = User(username='apiuser', password=random_string(8))
        user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def tearDown(self):
        remove_temp_folder()

    def test_upload_sample(self):
        """
        Ensure we can upload a new sample object.
        """
        url = reverse_lazy('sample-list')
        file_path = make_sample_file()
        with open(file_path, 'rb') as data:
            response = self.client.post(url, {'sample': data})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
