# -*- coding: utf-8 -*-

import unittest

from hamlish_jinja import Hamlish, Output

import testing_base


class TestDebugOutput(testing_base.TestCase):



    def setUp(self):
        self.hamlish = Hamlish(
            Output(indent_string='  ', newline_string='\n', debug=True))


    def test_html_tags(self):

        s = self._h('''


%html
    %head
        %title << Test
    %body

        %p
            Test




        %p << Test



        %p
            Test
''')
        r = '''


<html>
  <head>
    <title>Test</title></head>
  <body>

    <p>
      Test</p>




    <p>Test</p>



    <p>
      Test</p></body></html>
'''

        self.assertEqual(s, r)


    def test_jinja_tags(self):

        s = self._h('''

-macro test(name):
    %p << {{ name }}

-block content:


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

        -trans count=i:
            There is {{ count }} object.
        -pluralize
            There is {{ count }} objects.

    -else:
        Test
''')
        r = '''

{% macro test(name): %}
  <p>{{ name }}</p>{% endmacro %}

{% block content: %}


  {% for i in range(20): %}
    {% if i < 10: %}
      {{ test(i) }}
    {% elif i < 15: %}
      Test {{ i|safe }}
      {% if i == 10: %}
        Test
        {% continue %}


      {% elif i == 11: %}
        {% break %}{% endif %}

      Test

    {% else: %}
      Test{% endif %}

    {% trans count=i: %}
      There is {{ count }} object.
    {% pluralize %}
      There is {{ count }} objects.{% endtrans %}

  {% else: %}
    Test{% endfor %}{% endblock %}
'''

        self.assertEqual(s, r)





    def test_preformatted_lines(self):

        s = self._h('''
%html
    %pre
        |def test(name):
        |    if True:
        |        print name




    %p
        Test
''')
        r = '''
<html>
  <pre>
def test(name):
    if True:
        print name</pre>




  <p>
    Test</p></html>
'''
        self.assertEqual(s, r)


    def test_self_closing_tag_with_empty_lines_bellow(self):

        s = self._h('''
%br



%span << test''')

        r = '''
<br />



<span>test</span>
'''
        self.assertEqual(s, r)




    def test_nested_tags(self):

        s = self._h('''
%ul
    -for i in range(10):
        %li -> %a href="{{ i }}" << {{ i }}

    %span << test
''')
        r = '''
<ul>
  {% for i in range(10): %}
    <li><a href="{{ i }}">{{ i }}</a></li>{% endfor %}

  <span>test</span></ul>
'''
        self.assertEqual(s, r)

    def test_nested_tags2(self):

        s = self._h('''
%ul
    -for i in range(10):
        %li -> %a href="{{ i }}" -> {{ i }}

    %span << test
''')
        r = '''
<ul>
  {% for i in range(10): %}
    <li><a href="{{ i }}">{{ i }}</a></li>{% endfor %}

  <span>test</span></ul>
'''
        self.assertEqual(s, r)


    def test_nested_tags3(self):

        s = self._h('''
%ul
    -for i in range(10):
        %li -> %a href="{{ i }}" -> =i

    %span << test
''')
        r = '''
<ul>
  {% for i in range(10): %}
    <li><a href="{{ i }}">{{ i }}</a></li>{% endfor %}

  <span>test</span></ul>
'''
        self.assertEqual(s, r)


    def test_nested_tags4(self):

        s = self._h('''
%ul
    -for i in range(10):
        %li -> %a href="{{ i }}"
            Test {{ i }}

    %span << test
''')
        r = '''
<ul>
  {% for i in range(10): %}
    <li><a href="{{ i }}">
      Test {{ i }}</a></li>{% endfor %}

  <span>test</span></ul>
'''
        self.assertEqual(s, r)


if __name__ == '__main__':
    unittest.main()