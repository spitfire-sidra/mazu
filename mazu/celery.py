# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

app = Celery('mazu')
app.conf.update(
    BROKER_URL = 'mongodb://localhost:27017/widget',
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    CELERYBEAT_SCHEDULE = {
        'exec_widget_modules': {
            'task': 'widget.tasks.exec_widget_modules',
            'schedule': crontab(minute='*/3'),
        },
    }
)
