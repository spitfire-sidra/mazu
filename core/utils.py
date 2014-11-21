# -*- coding: utf-8 -*-
import hashlib
import binascii

import ssdeep

from core.objects import Hashes


def compute_hashes(buf):
    """
    To compute hashes of buff.
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
        hashes.append(cls(buff).hexdigest())
    hashes.append(ssdeep.hash(buff))
    return Hashes(*hashes)


def get_file_info(fp):
    """
    Get information of Django InMemoryUploadedFile.
    """
    info = dict()
    try:
        buf = fp.read()
    except Exception as e:
        logger.debug(e)
    else:
        hashes = compute_hashes(buf)
        info['md5'] = hashes.md5
        info['sha1'] = hashes.sha1
        info['sha256'] = hashes.sha256
        info['sha512'] = hashes.sha512
        info['ssdeep'] = hashes.ssdeep
        info['size'] = getattr(fp, 'size', 0)
        info['type'] = magic.from_buffer(buf)
        info['crc32'] = binascii.crc32(buf)
    return info
