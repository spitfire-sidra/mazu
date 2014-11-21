# -*- coding: utf-8 -*-
import logging
import hashlib
import binascii

import magic
import ssdeep

from models import Sample
from core.mongodb import connect_gridfs


logger = logging.getLogger(__name__)


def compute_hashes(buf):
    """ Compute hashes

    >>> compute_hashes('HelloWorld')
    """
    algorithms = ('md5', 'sha1', 'sha256', 'sha512')
    hashes = dict()
    for a in algorithms:
        hashes[a] = getattr(hashlib, a)(buf).hexdigest()
    return hashes


def compute_ssdeep(buf):
    """ Compute ssdeep

    >>> compute_ssdeep('HelloWorld')
    """
    return ssdeep.hash(buf)


def get_uploaded_file_info(fp):
    """ Get information of Django InMemoryUploadedFile
    """
    info = dict()
    try:
        buf = fp.read()
    except Exception as e:
        logger.debug(e)
        raise
    else:
        info.update(compute_hashes(buf))
        info.update({
            'size': getattr(fp, 'size', None),
            'type': magic.from_buffer(buf),
            'crc32': binascii.crc32(buf),
            'ssdeep': compute_ssdeep(buf),
        })
        return info


def is_malware_exists(sha256):
    if Sample.objects.filter(sha256=sha256).count() > 0:
        return True
    else:
        return False


def save_malware(buf, user=None, source=None):
    hashes = compute_hashes(buf)

    if not is_malware_exists(hashes['sha256']):
        columns = dict()
        columns.update(hashes)
        columns.update({
            'size': str(len(buf)), # bytes
            'type': magic.from_buffer(str(buf)),
            'crc32': binascii.crc32(buf),
            'ssdeep': compute_ssdeep(str(buf))
        })
        # save malware into gridfs
        try:
            gridfs = connect_gridfs()
        except:
            return False
        else:
            with gridfs.new_file() as fp:
                fp.write(str(buf))

                for attr, value in columns.items():
                    if attr != 'md5':
                        setattr(fp, attr, value)
                fp.close()
                columns['user'] = user
                columns['source'] = source
                instance = Sample(**columns)
                instance.save()
            return hashes['sha256']
