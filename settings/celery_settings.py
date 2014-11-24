# -*- coding: utf-8 -*-

CELERY_APPNAME = 'mazu'
CELERY_BROKER = 'mongodb://localhost:27017/widgets'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
