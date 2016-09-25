# -*- coding: utf-8 -*-

import unittest

from jinja2 import Environment, TemplateSyntaxError
from hamlish_jinja import Hamlish, Output, TemplateIndentationError, HamlishTagExtension

import testing_base




def simple_filter(text):
    return text

def simple_javascript_filter(text):
    return '<script type="text/javascript">\n'+text+'\n</script>'

filters={
    'testfilter': simple_filter,
    'javascript' : simple_javascript_filter,
}


# Used for running with the jinja environment
jinja_env = Environment(
    extensions = [
        HamlishTagExtension,
    ],
)

jinja_env.hamlish_mode='indented'
jinja_env.hamlish_indent_string='  '
jinja_env.hamlish_filters=filters

class TestFilters(testing_base.TestCase):

    def setUp(self):
        self.hamlish = Hamlish(
            Output(indent_string='  ', newline_string='\n'),
            filters={
                'testfilter': simple_filter,
                'javascript' : simple_javascript_filter,
            })


    def test_filter(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :testfilter
            Filtered text1,
                Filtered text2,
            Filtered text3.
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
Filtered text1,
    Filtered text2,
Filtered text3.
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)


    def test_filter_indented(self):
        s = self._h('''
%html
    %body
        %p -> Test
        %div
            :testfilter
                Filtered text1,
                    Filtered text2,
                Filtered text3.
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
    <div>
Filtered text1,
    Filtered text2,
Filtered text3.
    </div>
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)


    def test_filter_at_root_level(self):
        s = self._h('''
%html
    %body
        %p -> Test
:testfilter
    Filtered text1,
        Filtered text2,
    Filtered text3.
%div
    %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
  </body>
</html>
Filtered text1,
    Filtered text2,
Filtered text3.
<div>
  <p>Test</p>
</div>\
'''
        self.assertEqual(s, r)


    def test_filter_last(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :testfilter
            Filtered text1,
                Filtered text2,
            Filtered text3.
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
Filtered text1,
    Filtered text2,
Filtered text3.
  </body>
</html>\
'''
        self.assertEqual(s, r)

    def test_filter_startswith_whitespace(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :testfilter


            Filtered text1,
                Filtered text2,
            Filtered text3.
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>


Filtered text1,
    Filtered text2,
Filtered text3.
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)

    def test_filter_last_startswith_whitespace(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :testfilter


            Filtered text1,
                Filtered text2,
            Filtered text3.
''')
        r = '''\
<html>
  <body>
    <p>Test</p>


Filtered text1,
    Filtered text2,
Filtered text3.
  </body>
</html>\
'''
        self.assertEqual(s, r)


    # Whitespace at the end is stripped
    def test_filter_starts_ends_with_whitespace(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :testfilter


            Filtered text1,
                Filtered text2,
            Filtered text3.


        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>


Filtered text1,
    Filtered text2,
Filtered text3.
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)




    def test_filter_empty(self):
        self.assertRaises(TemplateSyntaxError,
                lambda: self._h('''
%html
    %body
        %p -> Test
        :testfilter
        %div
            %p -> Test
'''))


    def test_filter_empty2(self):
        self.assertRaises(TemplateSyntaxError,
                lambda: self._h('''
%html
    %body
        %p
            :testfilter
        %div
            %p -> Test
'''))



    def test_filter_last_empty(self):
        self.assertRaises(TemplateSyntaxError,
                lambda: self._h('''
%html
    %body
        %p -> Test
        :testfilter

'''))

    # Should be ignored and threated as plain text
    def test_filter_undefined(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :testundefinedfilter

            Filtered text1,
                Filtered text2,
            Filtered text3.

        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
    :testundefinedfilter
      Filtered text1,
        Filtered text2,
      Filtered text3.
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)


    def test_multiple_filters(self):
        s = self._h('''
%html
    %body
        %p -> Test
        %div
            :testfilter
                Filtered text1,
                Filtered text2,
            :testfilter
                Filtered text1,
                Filtered text2,
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
    <div>
Filtered text1,
Filtered text2,
Filtered text1,
Filtered text2,
    </div>
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)



    def test_multiple_filters2(self):
        s = self._h('''
%html
    %body
        %p -> Test
        %div
            :testfilter
                Filtered text1,
                Filtered text2,
            %p -> Test
            :testfilter
                Filtered text1,
                Filtered text2,
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
    <div>
Filtered text1,
Filtered text2,
      <p>Test</p>
Filtered text1,
Filtered text2,
    </div>
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)



    def test_filter_complex(self):
        s = self._h('''
%html
    %body
        %p -> Test
        %div
            :testfilter
                Filtered text1,
                    Filtered text2,
                        Filtered text1,
                      Filtered text1,
                Filtered text3.
                    Filtered text1,
                Filtered text1,
                               Filtered text1,
                test
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
    <div>
Filtered text1,
    Filtered text2,
        Filtered text1,
      Filtered text1,
Filtered text3.
    Filtered text1,
Filtered text1,
               Filtered text1,
test
    </div>
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)




    def test_filter_javascript(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :javascript
            $("#test").click(function(){
                alert('Test');
            });
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
<script type="text/javascript">
$("#test").click(function(){
    alert('Test');
});
</script>
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)


    def test_filter_with_jinja(self):
        s = self._h('''
%html
    %body
        %p -> Test
        :javascript
            $("#test").click(function(){
                alert({{var}});
            });
        %div
            %p -> Test
''')
        r = '''\
<html>
  <body>
    <p>Test</p>
<script type="text/javascript">
$("#test").click(function(){
    alert({{var}});
});
</script>
    <div>
      <p>Test</p>
    </div>
  </body>
</html>\
'''
        self.assertEqual(s, r)


    def test_inside_haml_tag(self):

        s = jinja_env.from_string(
'''{% haml %}
%div
    :testfilter
        Test
            Test
    %p
        test
{% endhaml %}
''')
        r = '''\
<div>
Test
    Test
  <p>
    test
  </p>
</div>'''

        self.assertEqual(s.render(),r)



if __name__ == '__main__':
    unittest.main()
