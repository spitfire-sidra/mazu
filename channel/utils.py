# -*- coding: utf-8 -*-
from models import Channel

def get_channels():
    mapping = dict()
    for c in Channel.objects.all():
        mapping.update({
            c.name: {
                'host': c.host,
                'port': c.port,
                'ident': c.ident,
                'secret': c.secret,
                'subchans': [c.subchans]
            }
        })
    return mapping
