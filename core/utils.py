# -*- coding: utf-8 -*-
import hashlib
import binascii
import logging

import ssdeep

from core.objects import Hashes

logger = logging.getLogger(__name__)


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


def dynamic_import(appname, foldername='modules'):
    """
    Import all classes under sub folder of app.
    >>> dynamic_import('samples', 'widgets')
    True
    """
    import pkgutil
    success = True
    folder_path = os.path.join(appname, foldername)
    class_names = [n for _, n, _ in pkgutil.iter_modules([folder_path])]
    for name in class_names:
        cls = '{}.{}.{}'.format(appname, foldername, name)
        try:
            __import__(cls, globals(), locals(), ['dummy'], -1)
        except ImportError as e:
            logger.debug(e)
            success = False
    return success
