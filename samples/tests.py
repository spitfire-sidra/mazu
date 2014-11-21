# -*- cofing: utf-8 -*-
import os

from django.core.urlresolvers import reverse_lazy

from models import Sample
from core.tests import CoreTestCase
from core.tests import random_string
from core.mongodb import connect_gridfs


def random_file():
    app_path = os.path.dirname(__file__)
    tests_folder = os.path.join(app_path, 'tests')
    if not os.path.exists(tests_folder):
        os.mkdir(tests_folder)

    path = os.path.join(app_path, 'tests', random_string(10))
    fp = open(path, 'wb')
    fp.write(random_string(10))
    fp.close()
    return path


class MalwareTestCase(CoreTestCase):

    def setUp(self):
        super(MalwareTestCase, self).setUp()
        self.file_path = random_file()
        self.file_name = random_string(8)

    def _upload(self, file_path, file_name):
        with open(file_path, 'rb') as fp:
            response = self.client.post(
                reverse_lazy('malware.upload'),
                {
                    #'name': file_name,
                    'malware': fp,
                    #'description': random_string(),
                },
                follow=True
            )
            return response

    def test_can_upload(self):
        # test can upload
        condition = {'filename': self.file_name}
        gridfs = connect_gridfs()
        excepted_count = gridfs.find(condition).count() + 1
        self._upload(self.file_path, self.file_name)
        count = gridfs.find(condition).count()
        self.assertEqual(count, excepted_count)

        # test can not upload repeatedly
        excepted_error = 'Duplicated Malware Sample.'
        response = self._upload(self.file_path, self.file_name)
        errors = response.context['form'].errors['malware']
        self.assertIn(excepted_error, errors)

    def test_list_view(self):
        self._upload(self.file_path, self.file_name)
        malwares = Sample.objects.all()
        response = self.client.get(reverse_lazy('malware.list'))
        self.assertEqual(response.status_code, 200)
        for mal in response.context['malwares']:
            self.assertIn(mal, malwares)

    def test_profile_view(self):
        self._upload(self.file_path, self.file_name)
        malware = Sample.objects.get(name=self.file_name)
        response = self.client.get(
            reverse_lazy('malware.profile', args=[malware.sha256])
        )
        self.assertEqual(response.context['malware'], malware)

    def test_can_update(self):
        self._upload(self.file_path, self.file_name)
        malware = Sample.objects.get(name=self.file_name)
        new_file_name = random_string(8)
        response = self.client.post(
            reverse_lazy('malware.update', args=[malware.sha256]),
            {
                #'name': new_file_name,
                'type': malware.type,
                'size': malware.size,
                'crc32': malware.crc32,
                'md5': malware.md5,
                'sha1': malware.sha1,
                'sha256': malware.sha256,
                'sha512': malware.sha512,
                'ssdeep': malware.ssdeep,
            }
        )
        try:
            Sample.objects.get(name=new_file_name)
        except Sample.DoesNotExist:
            updated = False
        else:
            updated = True
        self.assertTrue(updated)

    def test_can_delete(self):
        self._upload(self.file_path, self.file_name)
        malware = Sample.objects.get(name=self.file_name)
        self.client.post(
            reverse_lazy('malware.delete', args=[malware.sha256]),
            {
                'pk': malware.id
            }
        )
        try:
            Sample.objects.get(name=self.file_name)
        except Sample.DoesNotExist:
            does_exist = False
        else:
            does_exist = True
        self.assertFalse(does_exist)
