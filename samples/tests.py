# -*- cofing: utf-8 -*-
import os
import shutil

from django.core.urlresolvers import reverse_lazy

from core.mongodb import connect_gridfs
from core.tests import CoreTestCase
from core.tests import random_string
from core.utils import compute_hashes
from samples.models import Sample


def get_temp_folder():
    """
    Making a folder for testing
    """
    app_folder = os.path.dirname(__file__)
    temp_test_folder = os.path.join(app_folder, 'fake_samples')
    if not os.path.exists(temp_test_folder):
        os.mkdir(temp_test_folder)
    return temp_test_folder


def make_fake_sample_file():
    """
    Making a fake sample file for testing
    """
    temp_test_folder = get_temp_folder()
    fake_sample_path = os.path.join(temp_test_folder, random_string(10))
    with open(fake_sample_path, 'wb') as fp:
        fp.write(random_string(10))
    return fake_sample_path


def remove_temp_folder():
    """
    Removing temp folder
    """
    temp_folder = get_temp_folder()
    shutil.rmtree(temp_folder)


class SampleTestCase(CoreTestCase):

    """
    Test cases for Sample
    """

    def setUp(self):
        super(SampleTestCase, self).setUp()

    def tearDown(self):
        super(SampleTestCase, self).tearDown()
        remove_temp_folder()

    def upload_fake_sample(self, filepath=None):
        if not filepath:
            self.filepath = make_fake_sample_file()
            self.filename = random_string(8)
        else:
            self.filepath = filepath
        fp = open(self.filepath, 'rb')
        # compute hashes here
        self.hashes = compute_hashes(fp.read())
        # reset file pointer
        fp.seek(0)
        self.send_post_request(fp)
        fp.close()

    def send_post_request(self, fp):
        self.response = self.client.post(
            reverse_lazy('malware.upload'),
            {
                'sample': fp,
                #'name': filename,
                #'description': random_string(),
            },
            follow=True
        )

    def test_can_upload(self):
        # test can save sample in GridFS
        gridfs = connect_gridfs()
        self.upload_fake_sample()
        count = gridfs.find({'md5': self.hashes.md5}).count()
        self.assertGreater(count, 0)

        # test can not upload duplicated sample
        # use the same file which just created
        self.upload_fake_sample(self.filepath)
        response = self.get_response()
        expected_errors = 'Duplicated sample.'
        form_all_errors = response.context['form'].errors['sample']
        self.assertIn(expected_errors, form_all_errors)

    def test_list_view(self):
        target = reverse_lazy('malware.list')
        self.set_target(target)
        self.set_target_model(Sample)

        self.upload_fake_sample()
        self.assert_response_status_code(200)
        response = self.get_response()
        self.assert_response_objects_count(response, 'object_list')

    def test_profile_view(self):
        self.upload_fake_sample()
        sample = Sample.objects.get(sha256=self.hashes.sha256)
        response = self.client.get(
            reverse_lazy('malware.profile', args=[sample.sha256])
        )
        self.assertEqual(response.context['object'], sample)

    def test_can_update(self):
        self.upload_fake_sample()
        target = reverse_lazy('malware.update', args=[self.hashes.sha256])
        self.set_target(target)
        self.assert_response_status_code(200)
        random_filetype = random_string(8)
        sample = Sample.objects.get(sha256=self.hashes.sha256)
        response = self.client.post(
            reverse_lazy('malware.update', args=[self.hashes.sha256]),
            {
                'filetype': random_filetype,
                'size': sample.size,
                'crc32': sample.crc32,
                'md5': sample.md5,
                'sha1': sample.sha1,
                'sha256': sample.sha256,
                'sha512': sample.sha512,
                'ssdeep': sample.ssdeep,
            }
        )
        sample = Sample.objects.get(sha256=self.hashes.sha256)
        self.assertEqual(sample.filetype, random_filetype)

    def test_can_delete(self):
        self.upload_fake_sample()
        sample = Sample.objects.get(sha256=self.hashes.sha256)
        self.client.post(
            reverse_lazy('malware.delete', args=[sample.sha256]),
            {
                'pk': sample.id
            }
        )
        try:
            Sample.objects.get(sha256=self.hashes.sha256)
        except Sample.DoesNotExist:
            does_exist = False
        else:
            does_exist = True
        self.assertFalse(does_exist)
