# -*- coding: utf-8 -*-

import unittest

from jinja2 import TemplateSyntaxError
from hamlish_jinja import TemplateIndentationError

import testing_base

class TestSyntax(testing_base.TestCase):


    def test_mixed_tags_and_spaces(self):

        self.assertRaises(TemplateIndentationError,
                          lambda: self._h('''%div\n    \tTest'''))

    def test_indent_error(self):

        self.assertRaises(TemplateIndentationError,
                          lambda: self._h('''
%div
    %p
        Test
     %p
        Test
'''))

    def test_mixed_indent(self):

        try:
            self._h('''
%div
    %p
        Test
    %p
                %p
                    Test

    %p
            %p
                    Test
''')
        except TemplateIndentationError:
            self.fail('HamlishIndentationError raised')


    def test_continued_lines(self):

        s = self._h('''
%div style="background: red;\\
            color: blue; \\
            text-decoration: underline;"
    Test
''')
        r = '''\
<div style="background: red;color: blue; text-decoration: underline;">
  Test
</div>\
'''
        self.assertEqual(s, r)


    def test_continued_lines_jinja(self):

        s = self._h('''
-for i in [1,2,3,\\
        \t 4,5,6,7]:
    Test
''')
        r = '''\
{% for i in [1,2,3,4,5,6,7]: %}
  Test
{% endfor %}\
'''
        self.assertEqual(s, r)


    def test_escaped_line(self):

        s = self._h('''
\\-if 1 > 2:
    \\\Test
\\-else:
    Test
''')
        r = '''\
-if 1 > 2:
  \Test
-else:
  Test\
'''
        self.assertEqual(s, r)


    ##@unittest.Skip("Not supported")
    #def test_preformatted_lines_without_surrounding_tag(self):
        #"""Preformatted lines as only content whitout surrounding tag."""

        #s = self._h('''
#|    def test(name):
#|        if True:
#|            print name
#''')
        #r = '''\
    #def test(name):
        #if True:
            #print name\
#'''
        #self.assertEqual(s, r)


    def test_preformatted_inside_tag(self):

        s = self._h('''
%pre
    |def test(name):
    |    if True:
    |        print name
''')
        r = '''\
<pre>
def test(name):
    if True:
        print name
</pre>\
'''
        self.assertEqual(s, r)


    def test_ugly_pre_tag(self):
        """A ugly way to make a pre tag whitout leading and trailing whitespace when not using compact mode."""
        s = self._h('''
<pre>\\
def test(name):
|    print name\\
</pre>
''')
        r = '''\
<pre>def test(name):
    print name</pre>\
'''

        self.assertEqual(s, r)

if __name__ == '__main__':
    unittest.main()