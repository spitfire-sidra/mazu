# -*- coding: utf8 -*-
import re
import hashlib
from string import strip


# custom exception classes
class Disconnect(Exception):
    pass


class BadClient(Exception):
    pass


def hash(a, b):
    return hashlib.sha1('{0}{1}'.format(a, b)).digest()


def is_empty(s):
    res = strip(s, ' ')
    if res:
        return True
    return False


def custom_split(s):
    pattern = '[\s,;]'
    res = re.split(pattern, s)
    res = filter(is_empty, res)
    return res
