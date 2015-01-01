# -*- coding: utf-8 -*-
import os
import logging


logger = logging.getLogger(__name__)


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
