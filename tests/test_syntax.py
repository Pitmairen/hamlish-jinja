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


    def test_div_class_shortcut(self):
        s = self._h('''
.test
    Test
''')
        r = '''\
<div class="test">
  Test
</div>\
'''
        self.assertEqual(s, r)


    def test_div_class_shortcut_inline_data(self):
        s = self._h('''.test << Test''')
        r = '''<div class="test">Test</div>'''
        self.assertEqual(s, r)


    def test_div_id_shortcut(self):
        s = self._h('''
#test
    Test
''')
        r = '''\
<div id="test">
  Test
</div>\
'''
        self.assertEqual(s, r)


    def test_div_id_shortcut_inline_data(self):
        s = self._h('''#test << Test''')
        r = '''<div id="test">Test</div>'''
        self.assertEqual(s, r)



    def test_div_multiple_class_shortcut(self):
        s = self._h('''
.test.test2
    Test
''')
        r = '''\
<div class="test test2">
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_div_multiple_class_shortcut_inline_data(self):
        s = self._h('''.test.test2 << Test''')
        r = '''<div class="test test2">Test</div>'''
        self.assertEqual(s, r)


    def test_div_multiple_id_shortcut(self):
        s = self._h('''
#test#test2
    Test
''')
        r = '''\
<div id="test test2">
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_div_multiple_id_shortcut_inline_data(self):
        s = self._h('''#test#test2 << Test''')
        r = '''<div id="test test2">Test</div>'''
        self.assertEqual(s, r)


    def test_div_mixed_class_id_shortcut(self):
        s = self._h('''
#test.test
    Test
.test#test
    Test
.test#test.test2
    Test
#test.test#test2
    Test
#test#test2.test#test3.test2
    Test
''')
        r = '''\
<div id="test" class="test">
  Test
</div>
<div class="test" id="test">
  Test
</div>
<div class="test test2" id="test">
  Test
</div>
<div id="test test2" class="test">
  Test
</div>
<div id="test test2 test3" class="test test2">
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_div_multiple_id_shortcut_inline_data(self):
        s = self._h('''
#test.test << Test
.test#test << Test
.test.test2#test << Test
.test#test.test2 << Test
''')
        r = '''\
<div id="test" class="test">Test</div>
<div class="test" id="test">Test</div>
<div class="test test2" id="test">Test</div>
<div class="test test2" id="test">Test</div>\
'''
        self.assertEqual(s, r)


    def test_tag_class_shortcut(self):
        s = self._h('''
%div.test
    Test
''')
        r = '''\
<div class="test">
  Test
</div>\
'''
        self.assertEqual(s, r)




    def test_tag_class_shortcut_inline_data(self):
        s = self._h('''%div.test << Test''')
        r = '''<div class="test">Test</div>'''
        self.assertEqual(s, r)


    def test_tag_id_shortcut(self):
        s = self._h('''
%div#test
    Test
''')
        r = '''\
<div id="test">
  Test
</div>\
'''
        self.assertEqual(s, r)


    def test_tag_id_shortcut_inline_data(self):
        s = self._h('''%div#test << Test''')
        r = '''<div id="test">Test</div>'''
        self.assertEqual(s, r)



    def test_tag_multiple_class_shortcut(self):
        s = self._h('''
%div.test.test2
    Test
''')
        r = '''\
<div class="test test2">
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_tag_multiple_class_shortcut_inline_data(self):
        s = self._h('''%div.test.test2 << Test''')
        r = '''<div class="test test2">Test</div>'''
        self.assertEqual(s, r)


    def test_tag_multiple_id_shortcut(self):
        s = self._h('''
%div#test#test2
    Test
''')
        r = '''\
<div id="test test2">
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_tag_multiple_id_shortcut_inline_data(self):
        s = self._h('''%div#test#test2 << Test''')
        r = '''<div id="test test2">Test</div>'''
        self.assertEqual(s, r)


    def test_tag_mixed_class_id_shortcut(self):
        s = self._h('''
%div#test.test
    Test
%div.test#test
    Test
%div.test#test.test2
    Test
%div#test.test#test2
    Test
%div#test#test2.test#test3.test2
    Test
''')
        r = '''\
<div id="test" class="test">
  Test
</div>
<div class="test" id="test">
  Test
</div>
<div class="test test2" id="test">
  Test
</div>
<div id="test test2" class="test">
  Test
</div>
<div id="test test2 test3" class="test test2">
  Test
</div>\
'''
        self.assertEqual(s, r)

    def test_div_multiple_id_shortcut_inline_data(self):
        s = self._h('''
%div#test.test << Test
%div.test#test << Test
%div.test.test2#test << Test
%div.test#test.test2 << Test
''')
        r = '''\
<div id="test" class="test">Test</div>
<div class="test" id="test">Test</div>
<div class="test test2" id="test">Test</div>
<div class="test test2" id="test">Test</div>\
'''
        self.assertEqual(s, r)



    def test_mixed_shortcut_normal(self):
        s = self._h('''
#test class="test"
    Test
''')
        r = '''\
<div id="test" class="test">
  Test
</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal2(self):
        s = self._h('''
.test.test2 id="test"
    Test
''')
        r = '''\
<div class="test test2" id="test">
  Test
</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal3(self):
        s = self._h('''
%div#test class="test"
    Test
''')
        r = '''\
<div id="test" class="test">
  Test
</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal4(self):
        s = self._h('''
%div.test.test2 id="test"
    Test
''')
        r = '''\
<div class="test test2" id="test">
  Test
</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal_inline_data(self):
        s = self._h('''#test class="test" << Test''')
        r = '''<div id="test" class="test">Test</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal_inline_data2(self):
        s = self._h('''.test.test2 id="test" << Test''')
        r = '''<div class="test test2" id="test">Test</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal_inline_data3(self):
        s = self._h('''%div#test class="test" << Test''')
        r = '''<div id="test" class="test">Test</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal_inline_data4(self):
        s = self._h('''%div.test.test2 id="test" << Test''')
        r = '''<div class="test test2" id="test">Test</div>'''
        self.assertEqual(s, r)


    def test_shortcut_self_closing(self):
        s = self._h('''%div#test.''')
        r = '''<div id="test" />'''
        self.assertEqual(s, r)

    def test_shortcut_self_closing2(self):
        s = self._h('''%div#test.test.''')
        r = '''<div id="test" class="test" />'''
        self.assertEqual(s, r)

    def test_shortcut_self_closing3(self):
        s = self._h('''%div#test class="test".''')
        r = '''<div id="test" class="test" />'''
        self.assertEqual(s, r)




    def test_line_comment(self):
        s = self._h(''';Test''')
        r = ''
        self.assertEqual(s, r)


    def test_line_comment2(self):
        s = self._h('''
;%div
    %p << Test
''')
        r = '''\
<p>Test</p>\
'''
        self.assertEqual(s, r)

    def test_line_comment3(self):
        s = self._h('''
%html
    ;%body
        ;%div
            %p << Test
''')
        r = '''\
<html>
  <p>Test</p>
</html>\
'''
        self.assertEqual(s, r)

    def test_line_comment4(self):
        s = self._h('''
%html
    ;%body
        ;%div
            ;%p << Test
''')
        r = '''\
<html>
</html>\
'''
        self.assertEqual(s, r)

    def test_line_comment5(self):
        s = self._h('''
%html
    ;%body
        ;%div
    %p << Test
''')
        r = '''\
<html>
  <p>Test</p>
</html>\
'''
        self.assertEqual(s, r)

    def test_line_comment6(self):
        s = self._h('''
%html
    ;%body
        %div
            ;%ul
                ;%li << Test
            %ul
                %li << Test
''')
        r = '''\
<html>
  <div>
    <ul>
      <li>Test</li>
    </ul>
  </div>
</html>\
'''
        self.assertEqual(s, r)

    def test_line_comment_no_continued_line(self):
        s = self._h('''
%div
    ;Test \\
    %p << Test
''')
        r = '''\
<div>
  <p>Test</p>
</div>\
'''
        self.assertEqual(s, r)
if __name__ == '__main__':
    unittest.main()
