# -*- coding: utf-8 -*-
from django import template

from notification.models import Notification

register = template.Library()

# The first argument *must* be called "context" here.
def unreads(context, user):
    nots = Notification.objects.filter(read=False, user=user)[:5]
    context.update({'unreads': nots, 'unreads_count': len(nots)})
    return ''

register.simple_tag(takes_context=True)(unreads)
