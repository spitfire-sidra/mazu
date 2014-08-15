# -*- coding: utf-8 -*-
from django.test import TestCase

from utils import custom_split
from broker import Server 


class CustomSplitTestCase(TestCase):
    def setUp(self):
        self._test_cases()

    def _test_cases(self):
        res = ['a', 'b', 'c']
        self.test_cases = [
            ('a,b,c', res),
            ('a,b;c', res),
            ('a b c ', res),
            ('a, b, c', res),
            ('a , b, c,', res),
            ('  a  b  c  ', res)
        ]

    def test_split(self):
        for s, e in self.test_cases:
            res = custom_split(s)
            self.assertEqual(res, e)
