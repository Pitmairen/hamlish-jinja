# -*- coding: utf-8 -*-
#
# Copyright: (c) 2012 by Per Myren.
# License: BSD, see LICENSE for more details.
#

import re
import os.path

from jinja2 import TemplateSyntaxError, nodes
from jinja2.ext import Extension

__version__ = '0.3.3'


begin_tag_rx = r'\{%\-?\s*haml.*?%\}'
end_tag_rx = r'\{%\-?\s*endhaml\s*\-?%\}'

begin_tag_m = re.compile(begin_tag_rx)
end_tag_m = re.compile(end_tag_rx)


class HamlishExtension(Extension):

    def __init__(self, environment):
        super(HamlishExtension, self).__init__(environment)

        environment.extend(
            hamlish_mode='compact',
            hamlish_file_extensions=('.haml',),
            hamlish_indent_string='    ',
            hamlish_newline_string='\n',
            hamlish_debug=False,
            hamlish_enable_div_shortcut=False,
            hamlish_from_string=self._from_string
        )


    def preprocess(self, source, name, filename=None):
        if name is None or os.path.splitext(name)[1] not in \
            self.environment.hamlish_file_extensions:
            return source

        h = self.get_preprocessor(self.environment.hamlish_mode)
        try:
            return h.convert_source(source)
        except TemplateIndentationError as e:
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)
        except TemplateSyntaxError as e:
            raise TemplateSyntaxError(e.message, e.lineno, name=name, filename=filename)


    def get_preprocessor(self, mode):

        placeholders = {
            'block_start_string': self.environment.block_start_string,
            'block_end_string': self.environment.block_end_string,
            'variable_start_string': self.environment.variable_start_string,
            'variable_end_string': self.environment.variable_end_string}

        if mode == 'compact':
            output = Output(
                indent_string='',
                newline_string='',
                **placeholders)
        elif mode == 'debug':
            output = Output(
                indent_string='   ',
                newline_string='\n',
                debug=True,
                **placeholders)
        else:
            output = Output(
                indent_string=self.environment.hamlish_indent_string,
                newline_string=self.environment.hamlish_newline_string,
                debug=self.environment.hamlish_debug,
                **placeholders)

        return Hamlish(output, self.environment.hamlish_enable_div_shortcut)


    def _from_string(self, source, globals=None, template_class=None):
        env = self.environment
        globals = env.make_globals(globals)
        cls = template_class or env.template_class
        template_name = 'hamlish_from_string'
        if env.hamlish_file_extensions:
            template_name += env.hamlish_file_extensions[0]
        else:
            template_name += '.haml'
        return cls.from_code(env, env.compile(source, template_name), globals, None)


class HamlishTagExtension(HamlishExtension):

    tags = set(['haml'])


    def _get_lineno(self, source):
        matches = re.finditer(r"\n", source)
        if matches:
            return len(tuple(matches))
        return 0

    def parse(self, parser):

        haml_data = parser.parse_statements(['name:endhaml'])
        parser.stream.expect('name:endhaml')

        return [
            nodes.Output([haml_data])
        ]

    def preprocess(self, source, name, filename = None):
        ret_source = ''
        start_pos = 0

        while True:
            tag_match = begin_tag_m.search(source, start_pos)

            if tag_match:

                end_tag = end_tag_m.search(source, tag_match.end())

                if not end_tag:
                    raise TemplateSyntaxError('Expecting "endhaml" tag', self._get_lineno(source[:start_pos]))

                haml_source = source[tag_match.end() : end_tag.start()]

                h = self.get_preprocessor(self.environment.hamlish_mode)
                try:
                    ret_source += source[start_pos : tag_match.start()] + h.convert_source(haml_source)
                except TemplateIndentationError as e:
                    raise TemplateSyntaxError(e.message, e.lineno, name = name, filename = filename)
                except TemplateSyntaxError as e:
                    raise TemplateSyntaxError(e.message, e.lineno, name = name, filename = filename)

                start_pos = end_tag.end()
            else:
                ret_source += source[start_pos:]
                break

        return ret_source


class TemplateIndentationError(TemplateSyntaxError):
    pass


class Hamlish(object):

    INLINE_DATA_SEP = ' << '

    SELF_CLOSING_TAG = '.'
    JINJA_TAG = '-'
    JINJA_VARIABLE = '='
    HTML_TAG = '%'
    ESCAPE_LINE = '\\'
    PREFORMATED_LINE = '|'
    CONTINUED_LINE = '\\'
    ID_SHORTCUT = '#'
    CLASS_SHORTCUT = '.'
    LINE_COMMENT = ';'
    NESTED_TAGS_SEP = ' -> '



    #Which haml tags that can contain inline data
    _inline_data_tags = set([HTML_TAG, JINJA_TAG])

    #Which html tags that can start a line with nested tags
    _nested_tags = set([HTML_TAG, JINJA_TAG])


    _div_shorcut_re = re.compile(r'^(\s*)([#\.])', re.M)



    _self_closing_jinja_tags = set([
        'include', 'extends', 'import', 'set', 'from', 'do', 'break',
        'continue'
    ])

    _self_closing_html_tags = set([
        'br', 'img', 'link', 'hr', 'meta', 'input'
    ])


    _extended_tags = {
        'else' : set(['if', 'for']),
        'elif' : set(['if']),
        'pluralize' : set(['trans'])
    }


    def __init__(self, output, use_div_shortcut=False):
        self.output = output
        self._use_div_shortcut = use_div_shortcut

    def convert_source(self, source):

        tree = self.get_haml_tree(source)
        return self.output.create(tree)



    def get_haml_tree(self, source):

        blocks = self._get_haml_tree(source)
        return self._create_extended_jinja_tags(blocks)



    def _get_haml_tree(self, source):

        source_lines = self._get_source_lines(source)

        root = Node()

        # contains always atleast one element
        block_stack = [root]

        # stack for current indent level
        indent_stack = [-1]

        for lineno, line in enumerate(source_lines, 1):

            if not line.strip():
                block_stack[-1].add(EmptyLine())
                continue

            indent = 0
            m = re.match(r'^(\s+)', line)
            if m:
                indent = m.group(1)
                if ' ' in indent and '\t' in indent:
                    raise TemplateIndentationError('Mixed tabs and spaces', lineno)
                indent = len(indent)

            if indent > indent_stack[-1]:
                indent_stack.append(indent)
            else:
                while indent < indent_stack[-1]:
                    indent_stack.pop()
                    block_stack.pop()
                block_stack.pop()

            if indent != indent_stack[-1]:
                raise TemplateIndentationError('Unindent does not match any outer indentation level', lineno)


            node = self._parse_line(lineno, line.strip())

            if not block_stack[-1].can_have_children():

                if isinstance(node, InlineData):
                    raise TemplateSyntaxError('Inline Data Node can\'t contain child nodes', lineno)
                else:
                    raise TemplateSyntaxError('Self closing tag can\'t contain child nodes', lineno)

            block_stack[-1].add(node)
            block_stack.append(node)

        return root.children


    def _get_source_lines(self, source):

        if  self._use_div_shortcut:
            source = self._div_shorcut_re.sub(r'\1%div\2', source)

        lines = []

        # Lines that end with CONTINUED_LINE are merged with the next line
        continued_line = []

        for line in source.rstrip().split('\n'):

            line = line.rstrip()


            if line and line.lstrip()[0] == self.LINE_COMMENT:
                #Add empty line for debug mode
                lines.append('')

            elif line and line[-1] == self.CONTINUED_LINE:

                #If its not the first continued line we strip
                #the whitespace from the beginning
                if continued_line:
                    line = line.lstrip()

                #Strip of the CONTINUED_LINE character and save for later
                continued_line.append(line[:-1])

            elif continued_line:
                #If we have a continued line we join them together and add
                #them to the other lines
                continued_line.append(line.strip())
                lines.append(''.join(continued_line))

                #Add empty lines for debug mode
                lines.extend(['']*(len(continued_line)-1))

                #Reset
                continued_line = []
            else:
                lines.append(line)

        return lines


    def _parse_line(self, lineno, line):

        inline_data = None

        if self._has_inline_data(line):
            line, inline_data = self._parse_inline_data(line)

        if self._has_nested_tags(line):
            node = self._parse_nested_tags(lineno, line)
        else:
            node = self._parse_node(lineno, line)

        if inline_data is not None:

            if not node.can_have_children():
                raise TemplateSyntaxError('Node can\'t contain inline data', lineno)

            elif isinstance(node, NestedTags) and isinstance(node.nodes[-1], TextNode):
                raise TemplateSyntaxError('TextNode can\'t contain inline data', lineno)

            return InlineData(node, inline_data)
        return node


    def _parse_node(self, lineno, line):

        if line.startswith(self.HTML_TAG):
            return self._parse_html(lineno, line)
        elif line.startswith(self.JINJA_TAG):
            return self._parse_jinja(lineno, line)
        elif line.startswith(self.PREFORMATED_LINE):
            return PreformatedText(line[1:])
        elif line.startswith(self.JINJA_VARIABLE):
            return JinjaVariable(line[1:])
        elif line.startswith(self.ESCAPE_LINE):
            return TextNode(line[1:])

        return TextNode(line)


    def _has_inline_data(self, line):

        if line[0] not in self._inline_data_tags:
            return False

        return self.INLINE_DATA_SEP in line

    def _parse_inline_data(self, line):

        data = line.split(self.INLINE_DATA_SEP, 1)

        return data[0].rstrip(), data[1].lstrip()

    def _has_nested_tags(self, line):

        if line[0] not in self._nested_tags:
            return False

        return self.NESTED_TAGS_SEP in line

    def _parse_nested_tags(self, lineno, line):

        tags = line.split(self.NESTED_TAGS_SEP)

        nodes = []
        node_lines = [] #Used to make a nicer error message

        for line in [x.strip() for x in tags]:

            node = self._parse_node(lineno, line)

            if nodes and not nodes[-1].can_have_children():
                raise TemplateSyntaxError('Node "%s" can\'t contain children' % node_lines[-1], lineno)

            nodes.append(node)
            node_lines.append(line)

        return NestedTags(nodes)


    def _parse_html(self, lineno, line):

        m = re.match('^(\w+)(.*)$', line[1:])
        if m is None:
            raise TemplateSyntaxError(
                    'Expected html tag, got "%s".' % line, lineno)

        tag = m.group(1)
        attrs = m.group(2)


        self_closing = False
        if attrs and attrs[-1] == self.SELF_CLOSING_TAG:
            self_closing = True
            attrs = attrs[:-1].rstrip()
        elif tag in self._self_closing_html_tags:
            self_closing = True

        if attrs.startswith(self.ID_SHORTCUT) or \
            attrs.startswith(self.CLASS_SHORTCUT):

            attrs = self._parse_shortcut_attributes(attrs)

        elif attrs and attrs[0] == '(' and attrs[-1] == ')':
            attrs = ' ' + attrs[1:-1]

        if self_closing:
            return SelfClosingHTMLTag(tag, attrs)
        return HTMLTag(tag, attrs)


    def _parse_shortcut_attributes(self, attrs):
        orig_attrs = attrs
        value = attrs
        extra_attrs = ''

        # Extract extra attrs from parentheses, otherwise, split on first space
        m = re.match(r'^([\.#0-9A-Za-z\-]+)\((.+?)\)$', value)
        if m:
            value, extra_attrs = m.group(1), m.group(2)
        elif ' ' in value:
            value, extra_attrs = attrs.split(' ', 1)

        parts = re.split(r'([\.#])', value)

        #The first part should be empty
        parts = parts[1:]

        #Now parts should be a list like this ['.', 'value', '#', 'value']
        #So we take every second element starting from the first
        #and every second element starting from the second and zip them
        #together.
        parts = list(zip(parts[0::2], parts[1::2]))

        classes = []
        ids = []

        for type_, value in parts:

            if not value:
                #ignore empty values
                continue

            if type_ == self.CLASS_SHORTCUT:
                classes.append(value)
            else:
                ids.append(value)

        #We make the class and id the same order as in the template
        if orig_attrs.startswith(self.CLASS_SHORTCUT):
            attrs = (('class', classes), ('id', ids))
        else:
            attrs = (('id', ids), ('class', classes))

        rv = ' '.join('%s="%s"' % (k, ' '.join(v))
                for k, v in attrs if v)

        if extra_attrs:
            rv += ' ' + extra_attrs

        if rv:
            return ' ' + rv
        return rv



    def _parse_jinja(self, lineno, line):

        m = re.match('^(\w+)(.*)$', line[1:])
        if m is None:
            raise TemplateSyntaxError(
                    'Expected jinja tag, got "%s".' % line, lineno)

        tag = m.group(1)
        attrs = m.group(2)

        if tag in self._self_closing_jinja_tags:
            return SelfClosingJinjaTag(tag, attrs)

        elif tag in self._extended_tags:
            return ExtendingJinjaTag(tag, attrs)

        return JinjaTag(tag, attrs)



    def _create_extended_jinja_tags(self, nodes):
        """Loops through the nodes and looks for special jinja tags that
        contains more than one tag but only one ending tag."""

        jinja_a = None
        jinja_b = None
        ext_node = None
        ext_nodes = []

        for node in nodes:

            if isinstance(node, EmptyLine):
                continue


            if node.has_children():
                node.children = self._create_extended_jinja_tags(node.children)

            if not isinstance(node, JinjaTag):
                jinja_a = None
                continue

            if jinja_a is None or (
                node.tag_name in self._extended_tags and jinja_a.tag_name not in self._extended_tags[node.tag_name]):
                jinja_a = node
                continue


            if node.tag_name in self._extended_tags and \
                jinja_a.tag_name in self._extended_tags[node.tag_name]:

                if ext_node is None:
                    ext_node = ExtendedJinjaTag()
                    ext_node.add(jinja_a)
                    ext_nodes.append(ext_node)
                ext_node.add(node)

            else:
                ext_node = None
                jinja_a = node

        #replace the nodes with the new extended node
        for node in ext_nodes:
            nodes.insert(nodes.index(node.children[0]), node)

            index = nodes.index(node.children[0])
            del nodes[index:index+len(node.children)]

        return nodes





class Node(object):


    def __init__(self):
        self.children = []

    def has_children(self):
        "returns False if children is empty or contains only empty lines else True."
        return bool([x for x in self.children if not isinstance(x, EmptyLine)])


    def add(self, child):
        self.children.append(child)


    def can_have_children(self):
        return True

    def write(self, output, indent):
        pass



class EmptyLine(Node):
    "Used in debug mode."


class HTMLTag(Node):

    def __init__(self, tag_name, attrs):
        self.tag_name = tag_name
        self.attrs = attrs
        super(HTMLTag, self).__init__()


class JinjaTag(Node):

    def __init__(self, tag_name, attrs):
        self.tag_name = tag_name
        self.attrs = attrs
        super(JinjaTag, self).__init__()

class ExtendedJinjaTag(Node):
    pass


class TextNode(Node):
    def __init__(self, data):
        self.data = data
        super(TextNode, self).__init__()


class InlineData(Node):

    def __init__(self, node, data):
        self.node = node
        self.data = data
        super(InlineData, self).__init__()

    def can_have_children(self):
        return False

class NestedTags(Node):

    def __init__(self, nodes):
        self.nodes = nodes
        super(NestedTags, self).__init__()

    def can_have_children(self):
        #check if last node can have children
        return self.nodes[-1].can_have_children()

class PreformatedText(TextNode):
    pass


class SelfClosingTag(object):
    pass

class SelfClosingJinjaTag(JinjaTag, SelfClosingTag):

    def can_have_children(self):
        return False

class SelfClosingHTMLTag(HTMLTag, SelfClosingTag):

    def can_have_children(self):
        return False


class JinjaVariable(TextNode):
    pass


class ExtendingJinjaTag(JinjaTag, SelfClosingTag):
    pass



class Output(object):


    def __init__(self,
                 indent_string='    ',
                 newline_string='\n',
                 debug=False,
                 block_start_string='{%',
                 block_end_string='%}',
                 variable_start_string='{{',
                 variable_end_string='}}'):
        self._indent = indent_string
        self._newline = newline_string
        self.debug = debug
        self.buffer = []

        self.block_start_string = block_start_string
        self.block_end_string = block_end_string
        self.variable_start_string = variable_start_string
        self.variable_end_string = variable_end_string

    def reset(self):
        self.buffer = []

    def create(self, nodes):

        self.reset()

        self._create(nodes)

        if self.debug:
            return ''.join(self.buffer)
        return ''.join(self.buffer).strip()


    def write_self_closing_html(self, node):
        self.write('<%s%s />' % (node.tag_name, node.attrs))

    def write_open_html(self, node):
        self.write('<%s%s>' % (node.tag_name, node.attrs))

    def write_close_html(self, node):
        self.write('</%s>' % node.tag_name)

    def write_open_jinja(self, node):
        self.write('%s %s%s %s' % (
            self.block_start_string,
            node.tag_name,
            node.attrs,
            self.block_end_string))

    def write_close_jinja(self, node):
        self.write('%s end%s %s' % (
            self.block_start_string,
            node.tag_name,
            self.block_end_string))

    def write_jinja_variable(self, node):
        self.write('%s %s %s' % (
            self.variable_start_string,
            node.data,
            self.variable_end_string))

    def write_newline(self):
        self.write(self._newline)

    def write_indent(self, depth):
        self.write(self._indent * depth)

    def write(self, data):
        self.buffer.append(data)


    def write_open_node(self, node):
        if isinstance(node, JinjaTag):
            self.write_open_jinja(node)
        elif isinstance(node, NestedTags):
            for n in node.nodes:
                self.write_open_node(n)
        elif isinstance(node, SelfClosingHTMLTag):
            self.write_self_closing_html(node)
        elif isinstance(node, HTMLTag):
            self.write_open_html(node)
        elif isinstance(node, JinjaVariable):
            self.write_jinja_variable(node)
        elif isinstance(node, PreformatedText):
            self.write(node.data)
        elif isinstance(node, TextNode):
            self.write(node.data)


    def write_close_node(self, node):
        if isinstance(node, SelfClosingTag):
            return
        elif isinstance(node, NestedTags):
            for n in reversed(node.nodes):
                self.write_close_node(n)
        elif isinstance(node, JinjaTag):
            self.write_close_jinja(node)
        elif isinstance(node, HTMLTag):
            self.write_close_html(node)

        elif isinstance(node, ExtendedJinjaTag):
            self.write_close_node(node.children[0])


    def _create(self, nodes, depth=0):

        for node in nodes:

            if isinstance(node, EmptyLine):
                if self.debug:
                    self.write_newline()
                continue



            if isinstance(node, InlineData):
                self.write_indent(depth)
                self.write_open_node(node.node)
                self.write(node.data)
                self.write_close_node(node.node)
                self.write_newline()


            elif isinstance(node, ExtendedJinjaTag):

                for n in node.children:
                    self.write_indent(depth)
                    self.write_open_node(n)
                    self.write_newline()
                    if n.has_children():
                        self._create(n.children, depth+1)

            else:

                if not isinstance(node, PreformatedText):
                    self.write_indent(depth)
                self.write_open_node(node)

                if isinstance(node, SelfClosingTag):
                    self.write_newline()
                elif isinstance(node, PreformatedText):
                    self.write('\n')
                elif isinstance(node, (JinjaTag, HTMLTag, NestedTags)) and not node.has_children():
                    pass
                else:
                    self.write_newline()

            if node.children and not isinstance(node, ExtendedJinjaTag):
                self._create(node.children, depth+1)



            if self.debug:
                #Pop off all whitespace above this end tag
                #and save it to be appended after the end tag.
                prev = []
                while self.buffer[-1].isspace():
                    prev.append(self.buffer.pop())

            if isinstance(node, SelfClosingTag):
                pass
            elif isinstance(node, (JinjaTag, HTMLTag, ExtendedJinjaTag, NestedTags)):

                if not (self.debug or (isinstance(node, NestedTags) and not node.has_children())):
                    self.write_indent(depth)
                self.write_close_node(node)


                if not self.debug or (isinstance(node, NestedTags) and not node.has_children()):
                    self.write_newline()

            if self.debug:
                #readd the whitespace after the end tag
                self.write(''.join(prev))
