# -*- coding: utf-8 -*-

import unittest

from jinja2 import Environment

import testing_base

from hamlish_jinja import Hamlish, Output, HamlishExtension



class TestJinjaTags(testing_base.TestCase):

    def test_extends(self):

        s = self._h('''-extends "test.haml"''')
        r = '''{% extends "test.haml" %}'''

        self.assertEqual(s, r)

    def test_import(self):

        s = self._h('''-import "test.haml" as test''')
        r = '''{% import "test.haml" as test %}'''

        self.assertEqual(s, r)

    def test_from_import(self):

        s = self._h('''-from "test.haml" import test''')
        r = '''{% from "test.haml" import test %}'''

        self.assertEqual(s, r)

    def test_set(self):

        s = self._h('''-set i=1''')
        r = '''{% set i=1 %}'''

        self.assertEqual(s, r)

    def test_do(self):

        s = self._h('''-do test.append(1)''')
        r = '''{% do test.append(1) %}'''

        self.assertEqual(s, r)

    def test_continue(self):

        s = self._h('''-continue''')
        r = '''{% continue %}'''

        self.assertEqual(s, r)

    def test_break(self):

        s = self._h('''-break''')
        r = '''{% break %}'''

        self.assertEqual(s, r)

    def test_macro(self):
        s = self._h('''
-macro test(name):
    %p << {{ name }}
''')
        r = '''\
{% macro test(name): %}
  <p>{{ name }}</p>
{% endmacro %}\
'''
        self.assertEqual(s, r)


    def test_variable(self):

        s = self._h('''=test("test")''')
        r = '''{{ test("test") }}'''

        self.assertEqual(s, r)


    def test_inline_data(self):

        s = self._h('''-block title << Test''')
        r = '''{% block title %}Test{% endblock %}'''

        self.assertEqual(s, r)


    def test_empty_tag(self):
        s = self._h('''-block content''')
        r = '''{% block content %}{% endblock %}'''
        self.assertEqual(s, r)

    def test_if_elif(self):
        s = self._h('''
-if i < 10:
    Test
-elif i < 15:
    Test
''')
        r = '''\
{% if i < 10: %}
  Test
{% elif i < 15: %}
  Test
{% endif %}\
'''
        self.assertEqual(s, r)


    def test_if_elif_else(self):
        s = self._h('''
-if i < 10:
    Test
-elif i < 15:
    Test
-else:
    Test
''')
        r = '''\
{% if i < 10: %}
  Test
{% elif i < 15: %}
  Test
{% else: %}
  Test
{% endif %}\
'''
        self.assertEqual(s, r)

    def test_trans_pluralize(self):

        s = self._h('''
-trans count=i:
    There is {{ count }} object.
-pluralize:
    There is {{ count }} objects.
''')
        r = '''\
{% trans count=i: %}
  There is {{ count }} object.
{% pluralize: %}
  There is {{ count }} objects.
{% endtrans %}\
'''
        self.assertEqual(s, r)

    def test_nested_tags(self):
        s = self._h('''
-for i in range(20):
    -if i < 10:
        =test(i)
    -elif i < 15:
        Test {{ i|safe }}
        -if i == 10:
            Test
            -continue
        -elif i == 11:
            -break
        Test
    -else:
        Test
    Test
-else:
    Test
''')
        r = '''\
{% for i in range(20): %}
  {% if i < 10: %}
    {{ test(i) }}
  {% elif i < 15: %}
    Test {{ i|safe }}
    {% if i == 10: %}
      Test
      {% continue %}
    {% elif i == 11: %}
      {% break %}
    {% endif %}
    Test
  {% else: %}
    Test
  {% endif %}
  Test
{% else: %}
  Test
{% endfor %}\
'''

        self.assertEqual(s, r)




class TestJinjaTagsCustomPlaceholders(testing_base.TestCase):

    def setUp(self):
        self.hamlish = Hamlish(
            Output(indent_string='  ', newline_string='\n',
                  block_start_string='{$',
                  block_end_string='$}',
                  variable_start_string='${',
                  variable_end_string='}'
                  ))


    def test_custom_block_string(self):

        s = self._h('''-extends "test.haml"''')
        r = '''{$ extends "test.haml" $}'''

        self.assertEqual(s, r)

        s = self._h('''-block title -> Test''')
        r = '''{$ block title $}Test{$ endblock $}'''

        self.assertEqual(s, r)


    def test_custom_variable_string(self):

        s = self._h('''=test''')
        r = '''${ test }'''

        self.assertEqual(s, r)


    def _create_env(self):

        env = Environment(extensions=[HamlishExtension],
                         variable_start_string='${',
                         variable_end_string='}',
                         block_start_string='{$',
                         block_end_string='$}')
        env.hamlish_mode = 'indented'
        env.hamlish_indent_string = '  '

        return env

    def test_custom_variable_string_with_environment(self):

        env = self._create_env()


        s = env.hamlish_from_string('''\
%p
  =test''').render(test='123')
        r = '''\
<p>
  123
</p>'''

        self.assertEqual(s, r)



    def test_custom_block_string_with_environment(self):

        env = self._create_env()


        s = env.hamlish_from_string('''\
%ul
  -for i in [1,2,3]:
    %li -> =i
''').render()

        # Jinja adds some extra whitespace
        r = '''\
<ul>\n  \n    <li>1</li>\n  \n    <li>2</li>\n  \n    <li>3</li>\n  \n</ul>'''


        self.assertEqual(s, r)


if __name__ == '__main__':
    unittest.main()
