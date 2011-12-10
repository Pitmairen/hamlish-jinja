# -*- coding: utf-8 -*-

import unittest
import jinja2
from hamlish_jinja import Hamlish, Output, HamlishTagExtension

import testing_base


jinja_env = jinja2.Environment(
    extensions = [
        HamlishTagExtension,
    ]
)

class TestHamlTags(testing_base.TestCase):

    def setUp(self):
        self.hamlish = Hamlish(
            Output(indent_string='', newline_string='', debug=False))


    def test_basic(self):
        s = jinja_env.from_string(
'''{% haml %}
%div
    %p
        test
{% endhaml %}
''')
        r = u'''<div><p>test</p></div>'''
        self.assertEqual(s.render(),r)

    def test_multiple(self):
        s = jinja_env.from_string(
'''{% haml %}
%div
    %p
        test
{% endhaml %}
<div>hello</div>
{% haml %}
%div
    %p
        test
{% endhaml %}
''')
        r = u'''<div><p>test</p></div>\n<div>hello</div>\n<div><p>test</p></div>'''
        self.assertEqual(s.render(),r)
