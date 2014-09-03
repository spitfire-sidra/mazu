# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger


app = Celery('mazu')
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Execute modules under the widget app periodically.
app.conf.update(
    BROKER_URL = 'mongodb://localhost:27017/widget',
    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
    CELERYBEAT_SCHEDULE = {
        'exec-widget-modules': {
            'task': 'widget.tasks.exec_widget_modules',
            'schedule': crontab(minute='*/3'),
        },
        'exec-publisher': {
            'task': 'channel.tasks.publisher',
            'schedule': crontab(minute='*/3'),
        },
    }
)
