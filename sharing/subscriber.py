# -*- coding: utf-8 -*-
import os
import sys
import time
import datetime
import hashlib
import logging
from multiprocessing import Process

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")

from django.db import connection
from django.core.urlresolvers import reverse_lazy

from notification.models import Notification
from samples.utils import save_malware
from sharing.modules import hpfeeds
from sharing.utils import DictDiffer
from sharing.utils import get_channels



SUBJECT='YOU GOT A NEW MALWARE'
MESSAGE='YOU CAN VIEW DETAIL ABOUT THE MALWARE AT <a href="{}">{}</a>.'


INIT = None
CURRENT = None
PIDS = dict()


def create_hpc(host, port, ident, secret, subchans, user, source):
    def on_message(identifier, channel, payload):
        from django.db import connection
        connection.close()
        sha256 = save_malware(payload, user=user, source=source)
        link = reverse_lazy('malware.profile', args=[sha256])
        Notification(user=user, subject=SUBJECT, message=MESSAGE.format(link, sha256)).save()

    def on_error(payload):
        print >>sys.stderr, ' -> errormessage from server: {0}'.format(payload)
        hpc.stop()

    hpc = hpfeeds.new(host, port, ident, secret)
    hpc.subscribe(subchans)
    hpc.run(on_message, on_error)


def create_subscriber(host, port, ident, secret, subchans, user, source):
    p = Process(target=create_hpc, args=(host, port, ident, secret, subchans, user, source))
    p.start()
    return p


def handle_channels(added, removed, changed):
    """ Create, remove, update subscribers """
    global PIDS
    for key in added:
        c = CURRENT[key]
        p = create_subscriber(c['host'], c['port'], c['ident'], c['secret'], c['subchans'], c['user'], c['source'])
        PIDS.update({key: p})

    for key in removed:
        p = PIDS[key]
        p.terminate()
        del PIDS[key]

    for key in changed:
        p = PIDS[key]
        p.terminate()
        del PIDS[key]
        c = CURRENT[key]
        p = create_subscriber(c['host'], c['port'], c['ident'], c['secret'], c['subchans'])
        PIDS.update({key: p})


def main():
    global INIT
    global CURRENT
    global PIDS

    INIT = get_channels()
    for k, v in INIT.items():
        p = create_subscriber(v['host'], v['port'], v['ident'], v['secret'], v['subchans'], v['user'], v['source'])
        PIDS.update({k: p})

    while True:
        CURRENT = get_channels()
        if CURRENT != INIT:
            diff = DictDiffer(CURRENT, INIT)
            handle_channels(diff.added(), diff.removed(), diff.changed())
            INIT = CURRENT
        time.sleep(10)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
         #terminate all processes
         for k, v in PIDS.items():
             v.terminate()
         sys.exit(0)
