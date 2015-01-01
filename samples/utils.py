# -*- coding: utf-8 -*-
import os
import logging
import hashlib
import ssdeep
import binascii

from django.core.files.base import ContentFile

from core.mongodb import connect_gridfs
from core.mongodb import gridfs_delete_file
from core.utils import dynamic_import
from samples.models import Sample
from samples.models import Filetype
from samples.models import Description
from samples.objects import Hashes
from samples.filetypes.filetype import FileTypeDetector


logger = logging.getLogger(__name__)

# import all modules under the folder 'filetypes'
dynamic_import('samples', 'filetypes')


class FiletypeHelper(object):

    """
    A helper class helps you to get file types. You can customize a file type
    detector module. This helper class would try to load your module, and get
    the reuslt automatically.

    Usage:
    >>> file = open('photo.png')
    >>> file_type_helper = FiletypeHelper()
    >>> file_type_helper.identify(file.read())
    >>> file_types = file_type_helper.get_object_list()
    [
        'python-magic PNG image data...',
        '......'
    ]
    """

    def __init__(self):
        self.filetypes = list()
        self.object_list = list()

    def identify(self, content):
        """
        Getting all file types.
        """
        for module in FileTypeDetector.__subclasses__():
            filetype = module().from_file_content(content)
            self.filetypes.append(filetype)

    def get_or_create(self, filetype, detector):
        obj, created = Filetype.objects.get_or_create(
            filetype=filetype,
            detector=detector
        )
        return obj

    def get_object_list(self):
        for filetype, detector in self.filetypes:
            obj = self.get_or_create(filetype, detector)
            self.object_list.append(obj)
        return self.object_list


class SampleHelper(object):

    """
    A helper class handles sample related operations.
    """

    def __init__(self, fp):
        self.fp = fp
        self.size = self.get_size()
        self.content = self.get_content()
        self.crc32 = binascii.crc32(self.content)
        self.hashes = SampleHelper.compute_hashes(self.content)
        self.filetype_helper = FiletypeHelper()
        self.filetype_helper.identify(self.content)

    @staticmethod
    def compute_hashes(content):
        """
        To compute hashes of content.
        Available attributes as following:
        md5, sha1, sha256, sha512, ssdeep

        >>> hashes = make_hashes('123')
        >>> hashes.sha1
        '40bd001563085fc35165329ea1ff5c5ecbdbbeef'
        """
        argos = ('md5', 'sha1', 'sha256', 'sha512')
        hashes = list()
        for argo in argos:
            cls = getattr(hashlib, argo)
            hashes.append(cls(content).hexdigest())
        hashes.append(ssdeep.hash(content))
        return Hashes(*hashes)

    @staticmethod
    def payload_to_content_file(payload):
        """
        This method operates on string content (bytes also supported),
        rather than an actual file.
        It's possible that we only get the string content of malware
        rather than an actual file.

        https://docs.djangoproject.com/en/1.7/ref/files/file/

        Argus:
            payload - string (bytes also support)

        Returns:
            an instance of ContentFile
        """
        return ContentFile(payload)

    @staticmethod
    def sample_exists(sha256):
        """
        To check a sample is existing or not.

        Args:
            sha256 - a sha256 hash (string)

        >>> SampleHelper.sample_exists('73b49....')
        True
        """
        try:
            Sample.objects.get(sha256=sha256)
        except Sample.DoesNotExist:
            return False
        else:
            return True

    @staticmethod
    def gridfs_delete_sample(sha256):
        """
        Deleting a sample from GridFS which sha256 equals variable 'sha256'

        Args:
            sha256 - a sha256 hash (string)

        >>> SampleHelper.sample_exists('73b49....')
        True
        """
        return gridfs_delete_file('sha256', sha256)

    @staticmethod
    def append_filename(sample, filename):
        """
        Trying to append a filename to 'sample.filenames'.

        Args:
            sample - an instance of Sample
            filename - an instance of filename

        Returns:
            True - success
            False - failed
        """
        if not sample.filenames.filter(id=filename.id).exists():
            sample.filenames.add(filename)
            sample.save()
            return True
        return False

    @staticmethod
    def remove_filename(sample, filename):
        """
        Removing the filename instance form 'sample.filenames'.

        Args:
            sample - an instance of Sample
            filename - an instance of filename

        Returns:
            True - success
            False - failed
        """
        if sample.filenames.filter(id=filename.id).exists():
            sample.filenames.remove(filename)
            sample.save()
            return True
        return False

    @staticmethod
    def append_hyperlink(sample, hyperlink):
        """
        Trying to append a hyperlink to 'sample.hyperlinks'.

        Args:
            sample - an instance of Sample
            hyperlink - an instance of Hyperlink

        Returns:
            True - success
            False - failed
        """
        if not sample.hyperlinks.filter(id=hyperlink.id).exists():
            sample.hyperlinks.add(hyperlink)
            sample.save()
            return True
        return False

    @staticmethod
    def remove_hyperlink(sample, hyperlink):
        """
        Removing the hyperlink instance form 'sample.hyperlinks'.

        Args:
            sample - an instance of Sample
            hyperlink - an instance of Hyperlink

        Returns:
            True - success
            False - failed
        """
        if sample.hyperlinks.filter(id=hyperlink.id).exists():
            sample.hyperlinks.remove(hyperlink)
            sample.save()
            return True
        return False

    @staticmethod
    def append_source(sample, source):
        """
        Appending a Source to 'Sample.sources'.

        Args:
            sample - an instance of Sample
            source - an instance of Source

        Returns:
            True - success
            False - failed
        """
        if sample and source:
            if not sample.sources.filter(id=source.id).exists():
                sample.sources.add(source)
                sample.save()
                return True
        return False

    @staticmethod
    def remove_source(sample, source):
        """
        Remove 'source' from 'sample.sources'.

        Args:
            sample - an instance of sample
            source - an instance of source

        Returns:
            True - success
            False - failed
        """
        if sample and source:
            if sample.sources.filter(id=source.id).exists():
                sample.sources.remove(source)
                sample.save()
                return True
        return False

    @staticmethod
    def save_description(sample, text, user):
        """
        Saving description about a sample.

        Args:
            sample - an instance of Sample
            text - description
            user - an instance of User for marking who creates the description.

        Returns:
            True - success
            False - failed
        """
        if sample and text and user:
            try:
                descr = Description(sample=sample, text=text, user=user)
                descr.save()
            except Exception as e:
                logger.debug(e)
            else:
                return True
        return False

    def gridfs_save_sample(self, **kwargs):
        """
        Saving a sample into mongodb.

        You can pass any keyword arguments to this function.
        This function will try to save these keyword arguments as attributes
        of the sample.

        Keyword argument 'md5' would be ignored,
        because mongodb also saves md5 in GridFS.

        In mazu, we only save sha256 as an extra attribute.

        >>> helper = SampleHelper(open('thesample'))
        >>> helper.gridfs_save_sample(sha256='73b49....')
        True
        """
        ignored_attrs = ['md5']

        if SampleHelper.sample_exists(self.hashes.sha256):
            return False

        for k in ignored_attrs:
            try:
                kwargs.pop(k)
            except KeyError:
                pass

        try:
            gridfs = connect_gridfs()
        except Exception as e:
            logger.debug(e)
            return False
        else:
            with gridfs.new_file() as fp:
                fp.write(str(self.content))
                # save all attributes
                for attr, value in kwargs.items():
                    setattr(fp, attr, value)
            return True

    def get_size(self):
        """
        Trying to get the file size of the sample.
        """
        # if fp is an instance of InMemoryUploadedFile or ContentFile
        if hasattr(self.fp, 'size'):
            return self.fp.size

        if hasattr(self.fp, 'tell') and hasattr(self.fp, 'seek'):
            pos = self.fp.tell()
            self.fp.seek(0, os.SEEK_END)
            size = self.fp.tell()
            self.fp.seek(pos)
            return size
        return None

    def get_content(self):
        """
        Trying to get the content of the sample
        """
        if hasattr(self.fp, 'read') and hasattr(self.fp, 'tell') \
            and hasattr(self.fp, 'seek'):
            pos = self.fp.tell()
            content = self.fp.read()
            self.fp.seek(pos)
            return content
        return None

    def get_sample_attrs(self):
        """
        Trying to get attributes of the sample.
        """
        attrs = dict()
        attrs['md5'] = self.hashes.md5
        attrs['sha1'] = self.hashes.sha1
        attrs['sha256'] = self.hashes.sha256
        attrs['sha512'] = self.hashes.sha512
        attrs['ssdeep'] = self.hashes.ssdeep
        attrs['size'] = self.size
        attrs['crc32'] = self.crc32
        return attrs

    def save(self, user=None):
        """
        Saving a sample and its attributes.
        """
        attrs = self.get_sample_attrs()
        attrs['user'] = user
        if self.gridfs_save_sample():
            try:
                sample = Sample(**attrs)
                sample.save()
            except Exception:
                SampleHelper.gridfs_delete_sample(attrs['sha256'])
            else:
                sample.filetypes = self.filetype_helper.get_object_list()
                sample.save()
                return sample
        return False
