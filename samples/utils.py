# -*- coding: utf-8 -*-
import logging
import hashlib
import binascii

import magic
import ssdeep

from models import Sample
from core.mongodb import connect_gridfs
from core.mongodb import delete_file
from core.utils import compute_hashes


logger = logging.getLogger(__name__)


def get_file_attrs(fp):
    """
    Get attributes of Django InMemoryUploadedFile.
    """
    attrs = dict()
    try:
        buf = fp.read()
    except Exception as e:
        logger.debug(e)
    else:
        hashes = compute_hashes(buf)
        attrs['md5'] = hashes.md5
        attrs['sha1'] = hashes.sha1
        attrs['sha256'] = hashes.sha256
        attrs['sha512'] = hashes.sha512
        attrs['ssdeep'] = hashes.ssdeep
        attrs['size'] = getattr(fp, 'size', 0)
        attrs['type'] = magic.from_buffer(buf)
        attrs['crc32'] = binascii.crc32(buf)
        fp.seek(0)
    return attrs


def sample_exists(sha256):
    """
    To check a sample is existing or not.
    """
    try:
        Sample.objects.get(sha256=sha256)
    except Sample.DoesNotExist:
        return False
    else:
        return True


def save_sample(buf, **kwargs):
    """
    Saving a sample into mongodb.
    You can pass any keyword arguments to this function. This function will
    try to save these arguments as attributes of the sample. Keyword argument
    'md5' would be ignored, because mongodb also saves md5 in GridFS.

    >>> save_sample('HelloWorld!', user='spitfire', age='18 forever')
    True
    """
    ignored_attrs = ('md5')
    hashes = compute_hashes(buf)

    if sample_exists(hashes.sha256):
        return False

    try:
        gridfs = connect_gridfs()
    except Exception:
        return False
    else:
        with gridfs.new_file() as fp:
            fp.write(str(buf))
            # save all attributes
            for attr, value in kwargs.items():
                if attr not in ignored_attrs:
                    setattr(fp, attr, value)
        return True


def delete_sample(sha256):
    """
    Deleting a sample which sha256 equals variable 'sha256'
    """
    return delete_file('sha256', sha256)
