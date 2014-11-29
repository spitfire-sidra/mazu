# -*- coding: utf-8 -*-
import logging

from celery import shared_task

from core.mongodb import connect_gridfs
from sharing.modules import hpfeeds
from sharing.models import HPFeedsPubQueue


logger = logging.getLogger(__name__)


@shared_task
def hpfeeds_publish_sample(gridfs, sample_sha256, hpfeeds_channel):
    """
    Publishing a sample via HPFeeds.
    """
    for result in gridfs.find({'sha256': sample_sha256}, limit=1):
        sample = result

    if sample is None:
        return False

    try:
        hpc = hpfeeds.new(
            hpfeeds_channel.host,
            int(hpfeeds_channel.port),
            hpfeeds_channel.identity.encode(),
            hpfeeds_channel.secret.encode()
        )
    except Exception as e:
        logger.debug("Got an exception from HPFeeds: {0}".format(e))
        return False
    else:
        hpc.publish([hpfeeds_channel.pubchans], sample.read())
        error_message = hpc.wait()
        if error_message:
            logger.debug('Got an error from server: {0}'.format(error_message))
            return False
        else:
            return True


@shared_task
def check_hpfeeds_pubqueue():
    """
    Checks any unpublished sample exists. If it does exist, publish all
    unpublished samples via HPFeeds.
    """
    tasks = HPFeedsPubQueue.objects.filter(published=False)

    if tasks.count() < 1:
        return True

    try:
        gridfs = connect_gridfs()
    except Exception as e:
        logger.debug("Got an exception from GridFS: {0}".format(e))
        return False

    for task in tasks:
        if hpfeeds_publish_sample(gridfs, task.sample.sha256, task.channel):
            logger.debug("Sample #{0} published.".format(task.sample.id))
            task.published = True
            task.save()
    return True
