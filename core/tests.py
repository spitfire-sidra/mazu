# -*- cofing: utf-8 -*-
import random
import string
from StringIO import StringIO

from gridfs import GridFS

from django.test import Client
from django.test import TestCase
from django.contrib.auth.models import User

from mongodb import connect_gridfs
from mongodb import get_compressed_file
from mongodb import delete_file


def random_string(k=5):
    """
    Return a random string.
    Args:
        k - length of random string

    >>> random_sting()
    'YMluq'
    """
    choices = string.ascii_letters
    return ''.join([random.choice(choices) for i in range(k)])


def random_http_link():
    """
    Return a random http link.

    >>> random_http_link()
    'http://YMluq.example.com/'
    """
    return 'http://{0}.example.com/'.format(random_string())


class CoreTestCase(TestCase):

    """
    Core class of test case.
    """

    def setUp(self):
        self.username = random_string()
        self.password = random_string()
        self.user = User.objects.create_user(
            username=self.username,
            email='mazu@example.com',
            password=self.password
        )
        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def set_target(self, target):
        self.target = target

    def set_target_model(self, model):
        self.model = model

    def set_object_name(self, object_name):
        self.object_name = object_name

    def get_context_object(self, response, object_name=None):
        """
        Get context object. If the context object does not exist, return None.
        """
        if not object_name:
            object_name = self.object_name

        try:
            context_object = response.context[object_name]
        except KeyError:
            context_object = None
        return context_object

    def get_response(self):
        return self.response

    def try_get_context_object_count(self, response, object_name=None):
        """
        Try to get count of the context object. If a view has pagination,
        return the total records count of pagination first.
        """
        context_object = self.get_context_object(response, 'page_obj')
        if context_object:
            return context_object.paginator.count

        context_object = self.get_context_object(response, object_name)
        if context_object:
            return len(context_object)

    def assert_response_status_code(self, code):
        """
        Getting a view and asserting the status code.

        Return:
            response of a view
        """
        self.response = self.client.get(self.target)
        self.assertEqual(self.response.status_code, code)

    def assert_response_objects_count(self, response, object_name, **kwargs):
        """
        Asserting objects count of response.
        You can call assert_response_status_code(target, code) before invoke
        this method.

        Args:
            model - model class
            response - response of a view
        Kwargs:
            **kwargs - keyword arguments of filter method of model class
        """
        if kwargs:
            expected_count = self.model.objects.filter(**kwargs).count()
        else:
            expected_count = self.model.objects.all().count()
        count = self.try_get_context_object_count(response, object_name)
        self.assertEqual(count, expected_count)

    def send_post_request(self):
        self.response = self.client.post(
            self.target,
            self.post_data,
            follow=True
        )


class MongodbTestCase(TestCase):

    def setUp(self):
        self.fs = connect_gridfs()

    def test_connect_gridfs(self):
        self.assertIsInstance(self.fs, GridFS)

    def test_create_file(self):
        excepted_count = self.fs.find().count() + 1

        # creating a new file
        data = random_string()
        self.fs.put(data)

        count = self.fs.find().count()
        self.assertEqual(count, excepted_count)

    def test_download_zip(self):
        data = random_string()
        id = self.fs.put(data)
        output = get_compressed_file('_id', id)
        self.assertIsInstance(output, StringIO)

    def test_delete_file(self):
        data = random_string()
        id = self.fs.put(data)
        result = delete_file('_id', id)
        self.assertTrue(result)
