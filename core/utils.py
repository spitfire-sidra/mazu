# -*- coding: utf-8 -*-
import hashlib
import binascii

import ssdeep

from core.objects import Hashes


def compute_hashes(buff):
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
