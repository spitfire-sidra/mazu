# -*- coding: utf-8 -*-
"""
Experimental feature. This feature have not been tested.
"""
import os
import sys
import time
import logging
from multiprocessing import Process

# setup django environment
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)
sys.path.append(PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.production")

from django.contrib.auth.models import User

from samples.models import Sample
from samples.utils import SampleHelper
from extensions.hpfeeds.utils import DictDiffer
from extensions.hpfeeds.models import HPFeedsChannel
from extensions.hpfeeds.modules import hpfeeds


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
        mapping[key]['ident'] = chan.identity
        mapping[key]['secret'] = chan.secret
        mapping[key]['subchans'] = chan.get_subchans()
        mapping[key]['user_id'] = chan.user.id
        mapping[key]['source_id'] = getattr(chan.source, 'id', None)
    return mapping


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
        kwargs = current_subchans_mapping[key]
        proc = create_subscribe_process(**kwargs)
        subprocess_mapping.update({key: proc})

    for key in diff.removed():
        proc = subprocess_mapping[key]
        proc.terminate()
        del subprocess_mapping[key]

    for key in diff.changed():
        proc = subprocess_mapping[key]
        proc.terminate()
        del subprocess_mapping[key]
        kwargs = current_subchans_mapping[key]
        proc = create_subscribe_process(**kwargs)
        subprocess_mapping.update({key: proc})
    return True


def save_hpfeeds_payload(payload, user_id, source_id):
    """
    Save the payload received from hpfeeds
    """
    user = User.objects.get(id=user_id)
    content_file = SampleHelper.payload_to_content_file(payload)
    sample_helper = SampleHelper(content_file)
    if sample_helper.save(user=user):
        return True
    return False


def hpfeeds_client(host=None, port=None, ident=None, secret=None,
                   subchans=None, user_id=None, source_id=None):
    """
    Creating a hpfeeds client to subscribe message feeds from HPFeeds.
    """

    def on_message(ident, chanel, payload):
        """
        Because subprocess can not get the db connection of Django. We close
        the db connection here to force the subprocess get a new db connection.
        """
        from django.db import connection
        connection.close()
        save_hpfeeds_payload(payload, user_id, source_id)

    def on_error(payload):
        """
        Handling errors.
        """
        print >>sys.stderr, ' -> errormessage from server: {0}'.format(payload)
        hpfeeds_client.stop()

    hpfeeds_client = hpfeeds.new(host, port, ident, secret)
    hpfeeds_client.subscribe(subchans)
    hpfeeds_client.run(on_message, on_error)


def create_subscribe_process(**kwargs):
    """
    create a new process
    """
    proc = Process(target=hpfeeds_client, kwargs=kwargs)
    proc.start()
    return proc


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
        for _, process in subchans_mapping.items():
            process.terminate()
        sys.exit(0)
