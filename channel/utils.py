# -*- coding: utf-8 -*-
from models import Channel

def get_channels():
    mapping = dict()
    for c in Channel.objects.all():
        key = '{}-{}'.format(c.owner.id, c.name)
        mapping.update({
            key: {
                'host': c.host,
                'port': c.port,
                'ident': c.ident,
                'secret': c.secret,
                'subchans': [c.subchans],
                'user': c.owner,
                'source': c.source
            }
        })
    return mapping
