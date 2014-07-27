# -*- coding: utf-8 -*-
import gridfs
import zipfile
import logging

from StringIO import StringIO

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.errors import ConnectionFailure

from settings.mongodb import MONGOHOST
from settings.mongodb import MONGOPORT
from settings.mongodb import STORAGE


logger = logging.getLogger(__name__)

def connect_gridfs():
    """ Connect to GridFS

    >>> connect_gridfs()
    """
    try:
        mongodb = MongoClient(MONGOHOST, int(MONGOPORT))[STORAGE]
    except ConnectionFailure:
        raise ConnectionFailure
    except PyMongoError as e:
        logger.debug(e)
        raise
    except Exception as e:
        logger.debug(e)
        raise
    else:
        return gridfs.GridFS(mongodb)


def get_compressed_file(attr, value):
    """ Get a compressed file cursor that attribute equals specific value from GridFS

    >>> 
    """
    try:
        gridfs = connect_gridfs()
    except Exception as e:
        logger.debug(e)
        raise
    else:
        files = gridfs.find({attr: value})
        if files.count() > 0:
            zipdata = StringIO()
            zipfp = zipfile.ZipFile(zipdata, mode='w')
            zipfp.writestr(files[0].filename, files[0].read())
            zipfp.close()
            zipdata.seek(0)
            return zipdata
        else:
            return None


def delete_file(attr, value):
    """ Delete files in GridFS

    >>>
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
