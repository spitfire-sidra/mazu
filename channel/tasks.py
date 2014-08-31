# -*- coding: utf-8 -*-
import logging

from celery import shared_task

from lib import hpfeeds
from models import Queue
from core.mongodb import connect_gridfs


logger = logging.getLogger(__name__)


@shared_task
def publisher():
    jobs = Queue.objects.filter(published=False)
    try:
        gridfs = connect_gridfs()
    except Exception as e:
        logger.debug(e)

    for j in jobs:
        for r in gridfs.find({'sha256': j.malware.sha256}, limit=1):
            malware = r 

        try:
            hpc = hpfeeds.new(j.channel.host, int(j.channel.port), j.channel.ident.encode(), j.channel.secret.encode())
        except Exception as e:
            logger.debug(e)
        else:
            data = malware.read()
            hpc.publish([j.channel.pubchans], data)
            error_msg = hpc.wait()
            if error_msg:
                logger.debug('got error from server: {}'.format(error_msg))
            else:
                # also can add a notification
                j.published = True
                j.save()
