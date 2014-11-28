# -*- coding: utf-8 -*-
import logging

from celery import shared_task

from core.mongodb import connect_gridfs
from sharing.modules import hpfeeds
from sharing.models import HPFeedsPubQueue


logger = logging.getLogger(__name__)


@shared_task
def publisher():
    jobs = HPFeedsPubQueue.objects.filter(published=False)
    try:
        gridfs = connect_gridfs()
    except Exception as e:
        logger.debug(e)

    for j in jobs:
        for r in gridfs.find({'sha256': j.sample.sha256}, limit=1):
            sample = r

        try:
            hpc = hpfeeds.new(j.channel.host, int(j.channel.port), j.channel.identity.encode(), j.channel.secret.encode())
        except Exception as e:
            logger.debug(e)
        else:
            data = sample.read()
            hpc.publish([j.channel.pubchans], data)
            error_msg = hpc.wait()
            if error_msg:
                logger.debug('got error from server: {}'.format(error_msg))
            else:
                # also can add a notification
                j.published = True
                j.save()
