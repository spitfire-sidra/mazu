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

from lib import hpfeeds
from lib.dictdiffer import DictDiffer

from channel.utils import get_channels
from malware.utils import save_malware
from django.db import connection


INIT = None
CURRENT = None
PIDS = dict()


def create_hpc(host, port, ident, secret, subchans):
    
    def on_message(identifier, channel, payload):
        from django.db import connection
        connection.close()
        save_malware(payload)

    def on_error(payload):
        print >>sys.stderr, ' -> errormessage from server: {0}'.format(payload)
        hpc.stop()

    hpc = hpfeeds.new(host, port, ident, secret)
    hpc.subscribe(subchans)
    hpc.run(on_message, on_error)


def create_subscriber(host, port, ident, secret, subchans):
    p = Process(target=create_hpc, args=(host, port, ident, secret, subchans))
    p.start()
    return p


def handle_channels(added, removed, changed):
    """ Create, remove, update subscribers """
    global PIDS
    for key in added:
        c = CURRENT[key]
        p = create_subscriber(c['host'], c['port'], c['ident'], c['secret'], c['subchans'])
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
        p = create_subscriber(v['host'], v['port'], v['ident'], v['secret'], v['subchans'])
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