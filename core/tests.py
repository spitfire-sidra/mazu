# -*- cofing: utf-8 -*-
import random
import string


def random_string(k=5):
    """ Return a random string. Maximum value of k is 52.

        args:
            k - length of random string

    >>> random_sting()
    'YMluq'
    """
    if k >= 0 and k <= 52:
        return ''.join(random.sample(string.ascii_letters, k))
    else:
        return ''.join(random.sample(string.ascii_letters, 5))
