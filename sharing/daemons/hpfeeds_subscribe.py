# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
from multiprocessing import Process

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")

from django.db import connection
from django.core.urlresolvers import reverse_lazy

from notification.models import Notification
from samples.utils import save_sample
from sharing.modules import hpfeeds
from sharing.utils import DictDiffer
from sharing.models import HPFeedsChannel


SUBJECT = 'You got a new sample'
MESSAGE = 'You can view detail about the malware at <a href="{}">{}</a>.'


# used for storing hfpeeds client mapping
subchans_mapping = dict()
subprocess_mapping = dict()

def hpfeeds_subchans_mapping():
    """
    This function is used for making the kwargs of
    hpfeeds_client(**kwargs). Each channel has a key and kwargs mapping.
    This returned value is used for creating subprocesses.
    """
    mapping = dict()
    for chan in HPFeedsChannel.objects.all():
        key = '#{0}-{1}'.format(chan.user.username, chan.name)
        mapping[key] = dict()
        mapping[key]['host'] = chan.host
        mapping[key]['port'] = chan.port
        mapping[key]['identity'] = chan.identity
        mapping[key]['secret'] = chan.secret
        mapping[key]['subchans'] = [chan.subchans]
        mapping[key]['user'] = chan.user
        mapping[key]['source'] = chan.source
    return mapping



def hpfeeds_client(**kwargs):
    """
    Creating a hpfeeds client to subscribe message feeds from HPFeeds.
    """

    def on_message(identity, channel, payload):
        """
        Becasue subprocess can not get the db connection of Django. We close
        the db connection here to force the subprocess get a new db connection.
        """
        from django.db import connection
        connection.close()
        sha256 = save_sample(payload, user=user, source=source)
        link = reverse_lazy('malware.profile', args=[sha256])
        Notification(
            user=user, subject=SUBJECT, message=MESSAGE.format(link, sha256)
        ).save()

    def on_error(payload):
        """
        Handling errors.
        """
        print >>sys.stderr, ' -> errormessage from server: {0}'.format(payload)
        hpc.stop()

    host = kwargs.get('host', None)
    port = kwargs.get('port', None)
    identity = kwargs.get('identity', None)
    secret = kwargs.get('secret', None)
    subchans = kwargs.get('subchans', None)
    user = kwargs.get('user', None)
    source = kwargs.get('source', None)
    hpfeeds_client = hpfeeds.new(host, port, ident, secret)
    hpfeeds_client.subscribe(subchans)
    hpfeeds_client.run(on_message, on_error)


def create_subscribe_process(host, port, ident, secret, subchans, user, source):
    p = Process(target=hpfeeds_client, args=(
        host, port, ident, secret, subchans, user, source))
    p.start()
    return p


def subprocess_mapping_handler():
    """
    Create, remove, update subprocesses
    """
    global subchans_mapping
    global subprocess_mapping
    current_subchans_mapping = hpfeeds_subchans_mapping()

    if current_subchans_mapping == subchans_mapping:
        return True

    # if the HPFeedsChannel changed, update the subprocess_mapping
    subchans_mapping = current_subchans_mapping
    diff = DictDiffer(current_subchans_mapping, subchans_mapping)

    for key in diff.added():
        c = current_subchans_mapping[key]
        p = create_subscribe_process(c['host'], c['port'], c['ident'], c[
                              'secret'], c['subchans'], c['user'], c['source'])
        subprocess_mapping.update({key: p})

    for key in diff.removed():
        p = subprocess_mapping[key]
        p.terminate()
        del subprocess_mapping[key]

    for key in diff.changed():
        p = subprocess_mapping[key]
        p.terminate()
        del subprocess_mapping[key]
        c = current_subchans_mapping[key]
        p = create_subscribe_process(
            c['host'], c['port'], c['ident'], c['secret'], c['subchans'])
        subprocess_mapping.update({key: p})
    return True


def main():
    """
    All hpfeeds clients are running in subprocesses. Every ten secends this
    function checks any changes in HPFeedsChannel. If any changes exist,
    this function will add/update/terminate subprocesses.
    """
    global subchans_mapping
    global subprocess_mapping

    subchans_mapping = hpfeeds_subchans_mapping()
    for key, params in subchans_mapping.items():
        process = create_subscribe_process(**params)
        subprocess_mapping.update({key: process})

    while True:
        subprocess_mapping_handler()
        time.sleep(10)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        # terminate all processes
        for k, v in subchans_mapping.items():
            v.terminate()
        sys.exit(0)
