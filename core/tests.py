# -*- cofing: utf-8 -*-
import random
import string
from StringIO import StringIO

from gridfs import GridFS

from django.test import TestCase

from mongodb import connect_gridfs
from mongodb import get_compressed_file
from mongodb import delete_file


def random_string(k=5):
    """ Return a random string

        args:
            k - length of random string

    >>> random_sting()
    'YMluq'
    """
    choices = string.ascii_letters
    return ''.join([random.choice(choices) for i in range(k)])


class MongodbTestCase(TestCase):

    def setUp(self):
        self.fs = connect_gridfs()

    def test_connect_gridfs(self):
        self.assertIsInstance(self.fs, GridFS)

    def test_create_file(self):
        excepted_count = self.fs.find().count() + 1
        
        # create a new file
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
