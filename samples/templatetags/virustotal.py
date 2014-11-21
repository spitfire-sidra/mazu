# -*- coding: utf-8 -*-
from django import template


register = template.Library()


@register.filter
def virustotal_link(value, category='file'):
    if not category in ['file', 'url']:
        category = 'file'
    link = 'https://www.virustotal.com/en/{}/{}/analysis/'
    return link.format(category, value)
