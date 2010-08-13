# -*- coding: utf-8 -*-

import unittest

from jinja2 import TemplateSyntaxError

import testing_base


class TestHtmlTags(testing_base.TestCase):


    def test_content(self):

        s = self._h('''
%div
    Test
''')
        r = '''\
<div>
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_content_with_attributes(self):

        s = self._h('''
%div id="test" class="test"
    Test
''')
        r = '''\
<div id="test" class="test">
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_inline_content(self):

        s = self._h('''%div << Test''')
        r = '''<div>Test</div>'''

        self.assertEqual(s, r)

    def test_inline_content_with_attributes(self):

        s = self._h('''%div class="test" id="test" << Test''')
        r = '''<div class="test" id="test">Test</div>'''

        self.assertEqual(s, r)


    def test_empty_tags(self):

        s = self._h('''%div''')
        r = '''<div></div>'''

        self.assertEqual(s, r)

    def test_self_closing(self):

        s = self._h('''
%br.
%hr.
%meta name="description".
%div.
%div class="test".
''')
        r = '''\
<br />
<hr />
<meta name="description" />
<div />
<div class="test" />\
'''

        self.assertEqual(s, r)

    def test_auto_self_closing(self):

        s = self._h('''
%br
%hr
%meta name="description"
%input type="text"
%link rel="stylesheet"
%img src="test"
''')
        r = '''\
<br />
<hr />
<meta name="description" />
<input type="text" />
<link rel="stylesheet" />
<img src="test" />\
'''

        self.assertEqual(s, r)


    def test_invalid_self_closing(self):

        self.assertRaises(TemplateSyntaxError,
            lambda: self._h('''
%div.
    Test
'''))

    def test_invalid_self_closing_auto_close(self):

        self.assertRaises(TemplateSyntaxError,
            lambda: self._h('''
%br
    Test
'''))


    def test_invalid_self_closing_inline_data(self):

        self.assertRaises(TemplateSyntaxError,
            lambda: self._h('''
%div. << Test
'''))


    def test_invalid_self_closing_inline_data_auto_close(self):

        self.assertRaises(TemplateSyntaxError,
            lambda: self._h('''
%br << Test
'''))



        

if __name__ == '__main__':
    unittest.main()