# -*- coding: utf-8 -*-

import unittest

from hamlish_jinja import Hamlish, Output

import testing_base


class TestDebugOutput(testing_base.TestCase):



    def setUp(self):
        self.hamlish = Hamlish(
            Output(indent_string='', newline_string='', debug=False))


    def test_pre_tags(self):

        s = self._h('''
%pre
    |def test():
    |    if 1:
    |        print "Test"
''')
        r = '''<pre>def test():
    if 1:
        print "Test"
</pre>\
'''

        self.assertEqual(s, r)


if __name__ == '__main__':
    unittest.main()