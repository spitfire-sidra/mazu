# -*- coding: utf-8 -*-
import gridfs
import zipfile
import logging
from StringIO import StringIO

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.errors import ConnectionFailure

from settings.mongodb import MONGODB_HOST
from settings.mongodb import MONGODB_PORT
from settings.mongodb import MONGODB_STORAGE


logger = logging.getLogger(__name__)


def connect_gridfs():
    """
    Connect to GridFS.

    Args:
        None

    Returns:
        an instance of GridFS

    Raises:
        ConnectionFailure, PyMongoError, Exception

    >>> connect_gridfs()
    """
    try:
        mongodb = MongoClient(MONGODB_HOST, int(MONGODB_PORT))[MONGODB_STORAGE]
    except ConnectionFailure as e:
        logger.debug(e)
        raise ConnectionFailure
    except PyMongoError as e:
        logger.debug(e)
        raise
    except Exception as e:
        logger.debug(e)
        raise
    else:
        return gridfs.GridFS(mongodb)


def gridfs_get_zipfile(attr, value):
    """
    Get a zip file cursor that attribute equals specific value from GridFS

    Args:
        attr (str): The attribute to retrieve.
        vale (str): Value of the attribute.

    Returns:
        success - an instance of StringIO
        not found - None

    Raises:
        Exception

    >>> gridfs_get_zipfile('name', 'test')
    """
    try:
        gridfs = connect_gridfs()
    except Exception as e:
        logger.debug(e)
        raise
    else:
        files = gridfs.find({attr: value})
        # if multiple files returned.
        if files.count() > 0:
            zipdata = StringIO()
            zipfp = zipfile.ZipFile(zipdata, mode='w')
            # trying to set a filename for the file
            filename = getattr(files[0], 'sha256', files[0].md5)
            zipfp.writestr(filename, files[0].read())
            zipfp.close()
            zipdata.seek(0)
            return zipdata
        return None


def gridfs_delete_file(attr, value):
    """
    Delete files in GridFS

    Args:
        attr (str): The attribute to retrieve.
        vale (str): Value of the attribute.

    Returns:
        success - True
        not found - False

    Raises:
        Exception

    >>> gridfs_delete_file('name', 'test')
    """
    try:
        gridfs = connect_gridfs()
    except Exception as e:
        logger.debug(e)
        raise
    else:
        files = gridfs.find({attr: value})
        if files.count() > 0:
            for f in files:
                gridfs.delete(f._id)
            return True
        else:
            return False
