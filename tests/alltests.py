# -*- coding: utf-8 -*-

import unittest


if __name__ == '__main__':


    tests = [
        'test_debug_output', 'test_html_tags', 'test_jinja_tags',
        'test_syntax', 'test_div_shortcut', 'test_compact_output',
        'test_haml_tags'
    ]

    suite = unittest.TestLoader().loadTestsFromNames(tests)

    unittest.TextTestRunner().run(suite)
