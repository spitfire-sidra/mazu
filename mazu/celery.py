# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

from settings.celery_settings import CELERY_APPNAME
from settings.celery_settings import CELERY_BROKER
from settings.celery_settings import CELERY_RESULT_BACKEND


mazu_tasks = {
    'run_all_widgets': {
        'task': 'samples.tasks.run_all_widgets',
        'schedule': crontab(hour=21, minute=30),
    },
    'check_hpfeeds_pubqueue': {
        'task': 'extensions.hpfeeds.tasks.check_hpfeeds_pubqueue',
        'schedule': crontab(minute='*/3'),
    },
}

app = Celery(CELERY_APPNAME)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    BROKER_URL=CELERY_BROKER,
    CELERY_RESULT_BACKEND=CELERY_RESULT_BACKEND,
    CELERYBEAT_SCHEDULE=mazu_tasks
)
