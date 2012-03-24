========================
Hamlish-jinja
========================

Overview
========

This extension to jinja make it possible to use a haml-ish
syntax for your jinja templates.

It is implemented as a preprocessor and so it runs only
the first time your template is parsed. So it will not
affect the performance of your templates except for the first
run.

Usage
=====

Install
--------

You can install the latest version with
`easy_install <http://peak.telecommunity.com/DevCenter/EasyInstall>`_
or
`pip <http://pypi.python.org/pypi/pip>`_

::

    easy_install Hamlish-Jinja
    pip install Hamlish-Jinja


Basic Usage
-----------

To use this extension you just need to add it to you jinja
environment and use ".haml" as extension for your templates.

::

    from jinja2 import Environment
    from hamlish_jinja import HamlishExtension

    env = Environment(extensions=[HamlishExtension])


Configuration
-------------

The extension have some configuration options.
In the default configuration the output will be on
a single line, without whitespace, to save space.

hamlish_mode:
~~~~~~~~~~~~~

A string, it can be one of the following:

compact:
    Whitespace will be removed. This is the default

indented:
    The code will be nicely indented.

debug:
    The output will be similar to the haml syntax so that
    if you get a syntax error from jinja the debug message
    should display the correct line and source hint.


Example::
    env.hamlish_mode='debug'



hamlish_file_extensions:
~~~~~~~~~~~~~~~~~~~~~~~~

A list of file extensions to run the preprocessor on. The default
is ('.haml',)

Example::
    env.hamlish_file_extensions=('.haml',)


hamlish_enable_div_shortcut:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
*Added in version 0.2.0*

This enables the div shortcut so you can create div tags with a id or class
by using only the id (#myid) or class (.myclass) at the beginning of a line.

This is disabled by default.

Example::
    env.hamlish_enable_div_shortcut=True


Environment
-----------
*Added in version 0.2.0*

The environment gets extended with a new method **hamlish_from_string**
which works the same as the standard **env.from_string** method, but renders
the template with the hamlish preprocessor.

::

    tpl = '''
    %div
        %p
            test
    '''
    env.hamlish_from_string(tpl).render()


Syntax
======

The syntax is similar to haml.

You can use tabs or spaces for indentation, but you can't mix them
on the same line.
It is possible to mix tabs and spaces on separate lines if you
know what you are doing, but it's not recommended.


Html tags
---------

::

    %html
        %body
            %div
                Tag Content

::

    <html>
        <body>
            <div>
                Tag Content
            </div>
        </body>
    </html>


Html attributes
---------------

Attributes are just like normal html attributes.

::

    %div id="myid" class="myclass"
        Tag Content

::

    <div id="myid" class="myclass">
        Tag Content
    </div>


There is also a shortcut for creating classes and ids.
*Added in version 0.2.0*

::

    %div#myid.myclass
        Tag Content

::

    <div id="myid" class="myclass">
        Tag Content
    </div>

Multiple classes and ids can be chained together in
any order.

::

    %div#myid.myclass.myclass2
        Tag Content

::

    <div id="myid" class="myclass myclass2">
        Tag Content
    </div>


If these shortcuts are used at the beginning of a line and
*env.hamlish_enable_div_shortcut* is enabled a div is automatically created.

::

    #myid.myclass
        Tag Content

::

    <div id="myid" class="myclass">
        Tag Content
    </div>


Inline content
---------------

::

    %div << Tag Content

::

    <div>Tag Content</div>


Nested tags
---------------
*Added in version 0.2.0*

This is a shortcut to write multiple nested tags without
having to create a new line and indent level for each tag.

::

    %head
        %title -> -block title

    -for i in range(10):
        %li -> %a href={{ i }}" -> =i

::

    <head>
        <title>{% block title %}{% endblock %}</title>
    </head>

    {% for i in range(10): %}
        <li><a href="{{ i }}">{{ i }}</a></li>
    {% endfor %}


Self closing tags
-----------------

Tags can be closed by ending the line with a "."

Some tags ar automatically closed:
br, img, link, hr, meta, input

::

    %br
    %div.

::

    <br />
    <div />



Continued lines
----------------

Long lines can be split over many lines by ending the line with "\\"
The indent of the line after the "\\" will be ignored.

::

    %div style="background: red;\
            color: blue; \
            text-decoration: underline;"
        Tag Content

::

    <div style="background: red;color: blue; text-decoration: underline;">
        Tag Content
    </div>



Escaped lines
--------------

Lines that start with one of the special characters can
be escaped with "\\"

::

    \%div

::

    %div



Jinja tags
----------

Jinja tags starts with "-"

::

    -extends "layout.haml"

    %ul
        -for user in users:
            %li << {{ user }}
        -else:
            %li << No users

::

    {% extends "layout.haml" %}

    <ul>
        {% for user in users: %}
            <li>{{ user }}</li>
        {% else: %}
            <li>No users</li>
        {% endfor %}
    </ul>


Jinja Variables
---------------

Variables can be output directly in content by using the normal
{{ }} syntax.
or "=" can be used to output a variable on beginning of lines.

::

    -macro input(type, value):
        %input type="{{ type }}" value="{{ value }}".

    %form action="" method="post"
        %p
            =input(type="text", value="Test")

::

    {% macro input(type, value): %}
        <input type="{{ type }}" value="{{ value }}" />
    {% endmacro %}

    <form action="" method="post">
        <p>
            {{ input(type="text", value="Test") }}
        </p>
    </form>



Preformatted lines
------------------

::

    %pre
        |def test(name):
        |    print name

::

    <pre>
    def test(name):
        print name
    </pre>


Line comments
-------------
*Added in version 0.2.0*

Single lines can be commented by starting the line with a ";".
The lines will not be in the output.

::

    ;Test comment
    ;Test commnet
    %div
        ;%div
            Tag Content

::

    <div>
        Tag Content
    </div>


Example Template
================

::

    ;This is a test template
    ;to show the syntax
    -extends "base.haml"
    -import "lib/forms.haml" as forms

    -block title << Page Title

    -block content:
        -call forms.form_frame(form):
            %p
                =forms.input(form.username, type="text")
            %p
                =forms.input(form.password, type="password")
            %p
                %input type="submit" value="Login"


::

    {% extends "base.haml" %}
    {% import "lib/forms.haml" as forms %}

    {% block title %}Page Title{% endblock %}

    {% block content: %}
        {% call forms.form_frame(form): %}
            <p>
                {{ forms.input(form.username, type="text") }}
            </p>
            <p>
                {{ forms.input(form.password, type="password") }}
            </p>
            <p>
                <input type="submit" value="Login" />
            </p>
        {% endcall %}
    {% endblock %}


Hamlish Tag Extension
=====================
*Added in version 0.2.0*

This extension add a {% haml %}{% endhaml %} to jinja so you can embed
haml inside you html templates.


Usage
-----

To use this extension just add it to the jinja environment.

::

    from jinja2 import Environment
    from hamlish_jinja import HamlishTagExtension

    env = Environment(extensions=[HamlishTagExtension])


This extension uses the same configuration options as the HamlishExtension,
except that the env.hamlish_file_extensions option is not used.


Example
-------

::

    <html>
        <head><title>Example</title></head>
        <body>
        {% haml %}

        %form action="{{ action }}" method="post"
           -if form.has_errors():
              %ul.errors
                 -for err in form.errors:
                    %li -> =err

           %ul
              -for field in form:
                 %li -> =field

           %div.buttons
              %input type="submit" name="submit"
              %input type="submit" name="preview"

        {% endhaml %}
        </body>
    </html>


