# -*- coding: utf-8 -*-

import unittest

from hamlish_jinja import Hamlish, Output

import testing_base

class TestSyntax(testing_base.TestCase):

    def setUp(self):
        self.hamlish = Hamlish(
            Output(indent_string='  ', newline_string='\n'),
            use_div_shortcut=True)


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

    def test_mixed_shortcut_normal_inline_data(self):
        s = self._h('''#test class="test" << Test''')
        r = '''<div id="test" class="test">Test</div>'''
        self.assertEqual(s, r)

    def test_mixed_shortcut_normal_inline_data2(self):
        s = self._h('''.test.test2 id="test" << Test''')
        r = '''<div class="test test2" id="test">Test</div>'''
        self.assertEqual(s, r)


    def test_nested_with_shortcuts(self):
        s = self._h('''
%p -> %span.test
    Test
''')
        r = '''\
<p><span class="test">
  Test
</span></p>'''
        self.assertEqual(s, r)

    def test_nested_with_shortcuts2(self):
        s = self._h('''
%p -> %span.test << Test
''')
        r = '''\
<p><span class="test">Test</span></p>'''
        self.assertEqual(s, r)


    def test_nested_with_shortcuts3(self):
        s = self._h('''
%p -> %span.test id="test" -> Test
''')
        r = '''\
<p><span class="test" id="test">Test</span></p>'''
        self.assertEqual(s, r)

if __name__ == '__main__':
    unittest.main()

