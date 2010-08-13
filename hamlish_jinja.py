# -*- coding: utf-8 -*-

import re
import os.path


from jinja2 import  Environment, TemplateSyntaxError
from jinja2.ext import Extension


__version__ = '0.1.0'



class HamlishExtension(Extension):

    def __init__(self, environment):
        super(HamlishExtension, self).__init__(environment)

        environment.extend(
            hamlish_mode='compact',
            hamlish_file_extensions=('.haml',),
            hamlish_indent_string='    ',
            hamlish_newline_string='\n',
            hamlish_debug=False,
        )


    def preprocess(self, source, name, filename=None):
        if not os.path.splitext(name)[1] in \
            self.environment.hamlish_file_extensions:
            return source

        h = self.get_preprocessor(self.environment.hamlish_mode)
        try:
            return h.convert_source(source)
        except TemplateIndentationError, e:
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)
        except TemplateSyntaxError, e:
            raise TemplateSyntaxError(e.msg, e.lineno, name=name, filename=filename)


    def get_preprocessor(self, mode):

        if mode == 'compact':
            output = Output(indent_string='', newline_string='')
        elif mode == 'debug':
            output = Output(indent_string='   ', newline_string='\n')
        else:
            output = Output(indent_string=self.environment.hamlish_indent_string,
                        newline_string=self.environment.hamlish_newline_string)

        return Hamlish(output, mode == 'debug')



class TemplateIndentationError(TemplateSyntaxError):
    pass



class Hamlish(object):

    #Separator used  for inline block data
    INLINE_DATA_SEP = ' << '

    SELF_CLOSING_TAG = '.'
    JINJA_TAG = '-'
    JINJA_VARIABLE = '='
    HTML_TAG = '%'
    ESCAPE_LINE = '\\'
    PREFORMATED_LINE = '|'
    CONTINUED_LINE = '\\'


    # This is tags that can be continued on the same indent level
    # as the starting tag.
    # For example the "if" tag can have a "elif" or "else" on the same
    # indent level as the starting "if".
    extended_jinja_tags = set(['for', 'if', 'trans'])

    # This is the tags that can continue the extended tags above
    continued_jinja_tags = set(['else', 'elif', 'pluralize'])


    self_closing_jinja_tags = set([
        'include', 'extends', 'import', 'set', 'from', 'do', 'break',
        'continue',
    ])

    self_closing_html_tags = set([
        'br', 'img', 'link', 'hr', 'meta', 'input'
    ])



    def __init__(self, output, debug=False):
        self.output = output
        self.debug = debug


    def convert_source(self, source):

        blocks = self.get_haml_blocks(source.split('\n'))

        return self.create_output(blocks)


    def get_haml_blocks(self, source_lines):
        """Splits the haml formatted text into a list of blocks.

        A block is a tuple with this format:
            (lineno, linecontent, [sub blocks])
        """

        indent_levels = [-1]
        root = (-1, 'ROOT', [])
        block_stack = [root[2]]

        continued_line = None

        for lineno, line in enumerate(source_lines):
            lineno += 1

            if not line.strip():
                if self.debug:
                    block_stack[-1].append((lineno, '##empty_line##', ()))
                continue

            new_block = []

            if line[-1] == self.CONTINUED_LINE:
                if continued_line is None:
                    continued_line = (lineno, [line[:-1]], [])
                else:
                    continued_line[1].append(line.lstrip()[:-1])
                if self.debug:
                    continued_line[2].append((lineno, '##empty_line##', ()))
                continue
            elif continued_line is not None:
                continued_line[1].append(line.lstrip())

                lineno = continued_line[0]
                line = ''.join(continued_line[1])

                new_block = continued_line[2]
                continued_line = None



            indent = 0
            m = re.match(r'^(\s+)', line)
            if m:
                indent = m.group(1)
                if ' ' in indent and '\t' in indent:
                    raise TemplateIndentationError('Mixed tabs and spaces', lineno)

                indent = len(indent)


            if indent > indent_levels[-1]:
                indent_levels.append(indent)
            else:
                while indent < indent_levels[-1]:
                    indent_levels.pop()
                    block_stack.pop()

                block_stack.pop()

            if indent != indent_levels[-1]:
                raise TemplateIndentationError('Unindent does not match any outer indentation level', lineno)


            block_stack[-1].append((lineno, line.lstrip(), new_block))
            block_stack.append(new_block)

        return root[2]



    def create_output(self, blocks, depth=0):

        continued_block = None


        for block in blocks:


            if self.debug and block[1] == '##empty_line##':
                self.output.newline()
                continue
            #jinja tag
            elif block[1][0] == self.JINJA_TAG:

                continued_block = self.parse_jinja_block(block, depth,
                                                         continued_block)

            elif block[1][0] == self.JINJA_VARIABLE:

                continued_block = self.close_continued_block(continued_block, depth)

                if self.debug:
                    self.output.newline()

                self.output.indent(depth)

                self.output.write('{{ %s }}' % block[1][1:])

                if not self.debug:
                    self.output.newline()

                self.create_output(block[2], depth + 1)



            #html block
            elif block[1][0] == self.HTML_TAG:
                continued_block = self.close_continued_block(continued_block, depth)
                self.parse_html_block(block, depth)

            #preformated block
            elif block[1][0] == self.PREFORMATED_LINE:
                continued_block = self.close_continued_block(continued_block, depth)
                self.parse_preformated_block(block, depth)

            #data block
            else:
                continued_block = self.close_continued_block(continued_block, depth)

                if self.debug:
                    self.output.newline()
                self.output.indent(depth)

                if block[1][0] == self.ESCAPE_LINE:
                    self.output.write(block[1][1:])
                else:
                    self.output.write(block[1])
                if not self.debug:
                    self.output.newline()

                self.create_output(block[2], depth + 1)



        self.close_continued_block(continued_block, depth)


        if self.debug:
            return ''.join(self.output.output)[1:]
        return ''.join(self.output.output).strip()



    def close_continued_block(self, continued_block, depth):
        if continued_block is not None:
            self._close_block(depth, lambda: self.output.close_jinja(continued_block))



    def parse_jinja_block(self, block, depth, continued_block=None):

        line = block[1][1:]

        name = re.match('^(\w+)(.*)$', line).group(1)

        if continued_block is not None:
            if name not in self.continued_jinja_tags:
                continued_block = self.close_continued_block(continued_block, depth)

        if name in self.extended_jinja_tags:
            continued_block = name

        data = ''

        if self.INLINE_DATA_SEP in line:
            line, data = line.split(self.INLINE_DATA_SEP, 1)

        if self.debug:
            self.output.newline()

        self.output.indent(depth)
        self.output.open_jinja(name, line)

        if data:
            self.output.write(data)


        if name not in self.self_closing_jinja_tags and \
            continued_block is None and (data or not block[2]):
            self.output.close_jinja(name)

        if not self.debug: # and block[2]:
            self.output.newline()

        self.create_output(block[2], depth + 1)

        if not data and name not in self.self_closing_jinja_tags and continued_block is None\
            and block[2]:
            self._close_block(depth, lambda: self.output.close_jinja(name))


        if name in self.extended_jinja_tags:
            return name

        return continued_block



    def parse_html_block(self, block, depth):

        m = re.match('^(\w+)(.*)$', block[1][1:])

        tag = m.group(1)
        attrs = m.group(2)

        data = ''
        if self.INLINE_DATA_SEP in attrs:
            attrs, data = attrs.split(self.INLINE_DATA_SEP, 1)

        if self.debug:
            self.output.newline()

        self.output.indent(depth)


        self_closing = False

        if attrs and attrs[-1] == self.SELF_CLOSING_TAG:
            attrs = attrs[:-1]
            self_closing = True
        elif tag in self.self_closing_html_tags:
            self_closing = True

        attrs = attrs.rstrip()

        if self_closing and (data or block[2]):
            raise TemplateSyntaxError("Self closing tags can't have content", block[0])

        if self_closing:
            self.output.self_closing_html(tag, attrs)
        else:
            self.output.open_html(tag, attrs)

        if not self_closing and (data or not block[2]):
            if data:
                self.output.write(data)
            self.output.close_html(tag)

        if not self.debug:
            self.output.newline()

        self.create_output(block[2], depth + 1)

        if not data and not self_closing and block[2]:
            self._close_block(depth, lambda: self.output.close_html(tag))



    def parse_preformated_block(self, block, depth):

        if self.debug:
            self.output.write('\n')

        self.output.write(block[1][1:])

        if not self.debug:
            self.output.write('\n')

        self.create_output(block[2], depth + 1)


    def _close_block(self, depth, close_callback):
        if not self.debug:
            self.output.indent(depth)

        if self.debug:

            prev = []
            while self.output.output[-1].isspace():
                prev.append(self.output.output.pop())

        close_callback()

        if self.debug:
            self.output.write(''.join(prev))

        if not self.debug:
            self.output.newline()


class Output(object):

    def __init__(self, indent_string='  ', newline_string='\n'):
        self.output = []
        self.indent_string = indent_string
        self.newline_string = newline_string

    def open_html(self, tag, attrs):
        self.write('<%s%s>' % (tag, attrs and attrs))

    def close_html(self, tag):
        self.write('</%s>' % tag)

    def self_closing_html(self, tag, attrs):
        self.write('<%s%s />' % (tag, attrs and attrs))

    def open_jinja(self, tag, content):
        self.write('{%% %s %%}' % content)

    def close_jinja(self, tag):
        self.write('{%% end%s %%}' % tag)

    def indent(self, level):
        if level and self.indent_string:
            self.write(self.indent_string * level)

    def newline(self):
        if self.newline_string:
            self.write(self.newline_string)

    def write(self, data):
        self.output.append(data)


