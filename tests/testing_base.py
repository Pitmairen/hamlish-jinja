# -*- coding: utf-8 -*-

import unittest

from hamlish_jinja import Hamlish, Output


class TestCase(unittest.TestCase):

    def setUp(self):
        self.hamlish = Hamlish(
            Output(indent_string='  ', newline_string='\n'))

    def _h(self, source):
        return self.hamlish.convert_source(source)