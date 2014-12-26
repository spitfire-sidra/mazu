# -*- cofing: utf-8 -*-
import os
import shutil

from django.core.urlresolvers import reverse_lazy

from core.mongodb import connect_gridfs
from core.tests import CoreTestCase
from core.tests import random_string
from core.tests import random_integer
from core.tests import random_http_link
from core.utils import compute_hashes
from samples.utils import SampleHelper
from samples.models import Sample
from samples.models import Source
from samples.models import Filename


def get_temp_folder():
    """
    Making a folder for testing
    """
    app_folder = os.path.dirname(__file__)
    temp_test_folder = os.path.join(app_folder, 'fake_samples')
    if not os.path.exists(temp_test_folder):
        os.mkdir(temp_test_folder)
    return temp_test_folder


def make_sample_file():
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


class SourceTestCase(CoreTestCase):

    """
    Test cases for Source
    """

    def setUp(self):
        super(SourceTestCase, self).setUp()
        self.set_target_model(Source)

    def create_sample_source(self):
        target = reverse_lazy('source.create')
        self.set_target(target)
        self.random_post_data()
        self.send_post_request()

    def random_post_data(self):
        self.post_data = {
            'name': random_string(),
            'link': random_http_link(),
            'descr': random_string(),
        }

    def test_can_list(self):
        self.create_sample_source()
        target = reverse_lazy('source.list')
        self.set_target(target)
        self.assert_response_status_code(200)
        response = self.get_response()
        self.assert_response_objects_count(response, 'object_list')

    def test_can_create(self):
        count = self.model.objects.all().count()
        self.create_sample_source()
        excepted_count = self.model.objects.all().count()
        self.assertEqual(count + 1, excepted_count)

    def test_can_update(self):
        self.create_sample_source()
        source = self.model.objects.latest('created')
        target = reverse_lazy('source.update', kwargs={'pk': source.pk})
        self.set_target(target)
        self.random_post_data()
        self.send_post_request()
        source = self.model.objects.latest('created')
        for k, v in self.post_data.items():
            self.assertEqual(getattr(source, k), v)

    def test_can_delete(self):
        self.create_sample_source()
        source = self.model.objects.latest('created')
        target = reverse_lazy('source.delete', kwargs={'pk': source.pk})
        self.set_target(target)
        self.post_data = {'pk': source.pk}
        self.send_post_request()
        try:
            self.model.objects.get(pk=source.pk)
        except self.model.DoesNotExist:
            delete = True
        else:
            delete = False
        self.assertEqual(delete, True)

    def test_can_display_detail(self):
        self.create_sample_source()
        source = self.model.objects.latest('created')
        target = reverse_lazy('source.detail', kwargs={'pk': source.pk})
        self.set_target(target)
        self.assert_response_status_code(200)


class SampleTestCase(CoreTestCase):

    """
    Test cases for Sample
    """

    def setUp(self):
        super(SampleTestCase, self).setUp()
        self.helper = SampleHelper

    def tearDown(self):
        super(SampleTestCase, self).tearDown()
        remove_temp_folder()

    def random_post_data(self, fp):
        self.post_data = {
            'sample': fp,
            'share': False,
            'source': '',
            'filename': random_string(),
            'description': random_string(),
        }

    def upload_sample(self, filepath=None):
        if not filepath:
            self.filepath = make_sample_file()
            self.filename = random_string(8)
        else:
            self.filepath = filepath

        fp = open(self.filepath, 'rb')
        self.hashes = compute_hashes(fp.read())
        fp.seek(0)
        target = reverse_lazy('sample.upload')
        self.set_target(target)
        self.random_post_data(fp)
        self.send_post_request()
        fp.close()

    def test_can_upload(self):
        # test can save sample in GridFS
        gridfs = connect_gridfs()
        self.upload_sample()
        count = gridfs.find({'md5': self.hashes.md5}).count()
        self.assertGreater(count, 0)

        # test can not upload duplicated sample
        # use the same file which just created
        self.upload_sample(self.filepath)
        response = self.get_response()
        expected_errors = 'Duplicated sample.'
        form_all_errors = response.context['form'].errors['sample']
        self.assertIn(expected_errors, form_all_errors)

    def test_list_view(self):
        self.upload_sample()
        target = reverse_lazy('sample.list')
        self.set_target(target)
        self.set_target_model(Sample)
        self.assert_response_status_code(200)
        response = self.get_response()
        self.assert_response_objects_count(response, 'object_list')

    def test_detail_view(self):
        self.upload_sample()
        sample = Sample.objects.get(sha256=self.hashes.sha256)
        target = reverse_lazy(
            'sample.detail',
            kwargs={'sha256': sample.sha256}
        )
        self.set_target(target)
        self.assert_response_status_code(200)
        response = self.get_response()
        self.assertEqual(response.context['object'], sample)

    def test_can_delete(self):
        self.upload_sample()
        sample = Sample.objects.get(sha256=self.hashes.sha256)
        target = reverse_lazy('sample.delete', kwargs={'sha256':sample.sha256})
        self.set_target(target)
        self.post_data = {'pk': sample.pk}
        self.send_post_request()
        self.assertFalse(self.helper.sample_exists(sample.sha256), False)


class FilenameTestCase(CoreTestCase):

    """
    Test cases for Filename
    """

    def setUp(self):
        super(FilenameTestCase, self).setUp()
        self.post_data = dict()
        self.make_sample()

    def make_sample(self):
        """
        To make a sample for testing.
        """
        self.sample = Sample(
            md5=random_string(32),
            sha1=random_string(40),
            sha256=random_string(64),
            sha512=random_string(128),
            crc32=random_integer(),
            user=self.user
        )
        self.sample.save()

    def make_filename(self):
        """
        To make a filename for testing.
        """
        self.filename = Filename(name=random_string(), user=self.user)
        self.filename.save()

    def append_filename_to_sample(self):
        self.sample.filenames.add(self.filename)
        self.sample.save()

    def random_post_data(self):
        self.filename = random_string()
        self.post_data = {
            'filename': self.filename,
            'sample': self.sample.sha256
        }

    def test_can_append(self):
        target = reverse_lazy(
            'filename.append',
            kwargs={'sha256': self.sample.sha256}
        )
        self.set_target(target)
        self.assert_response_status_code(200)
        self.random_post_data()
        self.send_post_request()
        self.assert_response_status_code(200)
        count = Filename.objects.filter(name=self.filename).count()
        self.assertEqual(count, 1)

    def test_can_remove(self):
        self.make_filename()
        self.append_filename_to_sample()
        target = reverse_lazy(
            'filename.remove',
            kwargs={
                'sha256': self.sample.sha256,
                'filename_pk': self.filename.id
            }
        )
        self.set_target(target)
        self.assert_response_status_code(200)
        self.post_data['sample'] = self.sample.sha256
        self.post_data['filename'] = self.filename.id
        self.send_post_request()
        result = self.sample.filenames.filter(id=self.filename.id).exists()
        self.assertEqual(result, False)

    def test_can_delete(self):
        self.make_filename()
        target = reverse_lazy(
            'filename.delete',
            kwargs={
                'pk': self.filename.id
            }
        )
        self.set_target(target)
        self.assert_response_status_code(200)
        self.post_data['filename'] = self.filename.id
        self.send_post_request()
        count = Filename.objects.all().count()
        self.assertEqual(count, 0)
