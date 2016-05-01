#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This extension to jinja make it possible to use a
`haml <http://haml.info/>`_-ish syntax for your jinja2 templates.

Example template::

    -extends 'base.html'
    -block title << Memberlist
    -block content:
       %ul id="memberlist"
          -for user in users:
             %li
                %a href="{{ user.url }}" << {{ user.username }}

For more information read the
`documentation <http://github.com/Pitmairen/hamlish-jinja>`_
"""


from setuptools import setup

setup(
    name='Hamlish-Jinja',
    version='0.3.3',
    description='Haml-ish syntax for jinja2 templates',
    long_description=__doc__,
    author='Per Myren',
    author_email='progrper@gmail.com',
    url='http://github.com/Pitmairen/hamlish-jinja',
    py_modules=['hamlish_jinja'],
    install_requires=['Jinja2'],
    zip_safe=False,
    keywords = "jinja2 templates haml",
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
)
