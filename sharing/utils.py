# -*- coding: utf-8 -*-
from models import HPFeedsHPFeedsChannel

def get_channels():
    mapping = dict()
    for c in HPFeedsHPFeedsChannel.objects.all():
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
