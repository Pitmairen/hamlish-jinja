#! /usr/bin/python
#
# Copyright (C) 2011 Martin Andrews
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re
import sys

"""
This utility has a very limited scope : It parses the output of regular the 'Ruby' html2haml utility into the hamlish-jinja dialect.

A limited amount of testing shows that (despite its shortcomings) this utility can greatly increase the speed of implementing bought themes in Flask, for instance.

Known shortcomings:

    * This understands html2haml output - human created haml is probably too advanced to be translated reliably
    
    * Since html2haml doesn't understand embedded Ruby, this utility doesn't attempt to either
    
    * html2haml appears to mangle HTML5 doctypes - so these need to be manually fixed up at the top of the output
    
    * The special case of IE-version specific comments causes this to create a 'FIXME'
    
    * If something can't be parsed, then a 'FIXME' gets into the output
    
Typical Usage:: 

html2haml index.html | python haml2hamlish.py > index-in-hamlish-dialect.haml

"""

for line in sys.stdin:
    command = re.match( r'^(\s*)(.+?)(/?)$', line)
    
    indent = command.group(1)
    
    content = command.group(2)
    
    ending = ''
    if len(command.group(3))>0:
        ending = '.'
    
    first = ''
    if len(content)>0:
        first = content[0]
    
    if first in '%.#': 
        # This is a command - parse off the token at the beginning and read off the arguments if there's a {} group
        
        # Format is either : (a) TOKEN stuff, or (b) TOKEN{PARAM} stuff, where TOKEN contains no '{' or ' '
        
        args = re.match( r'^([^\{\s]*)(.*)$', content)
        token = args.group(1)
        parameters = ''
        remainder = args.group(2)
        if len(remainder)>0 and remainder[0] == '{': 
            # This command has a group of parameters after it
            # This will shrink as stuff is taken off the front
            parseme = remainder[1:]  # Still need to disgard a '}'

            # Take off groups that look like : PARAM => STRING[,}] where PARAM is either :SOMETHING or "SOMETHING"
            
            more = True
            while more:
                colon_match = re.match( r'^[\s,]*\:([^\s\=]*)\s*\=\>\s*"([^\"]*)"(.*)$', parseme)
                quote_match = re.match( r'^[\s,]*"([^\"]*)"\s*\=\>\s*"([^\"]*)"(.*)$', parseme)
                found_match = colon_match or quote_match
                if found_match:
                    parameters = parameters + ' ' + found_match.group(1) + '="' + found_match.group(2) +'"'
                    parseme = found_match.group(3)  # Ahah
                        
                else:
                    more = False
            remainder = parseme 
            
            # parameters should contain the parameters
            # remainder should be rest of line
            if len(remainder)>0 and remainder[0]=='}':
                remainder=remainder[1:] # Safe to forget first character
            else:
                print "THIS IS UNPARSED - FIXME :: " + remainder
            
        else:
            # This this is a simple token, rest of line is just content
            pass
            
        if remainder:
            remainder = ' << ' + remainder
            
        print indent + token + parameters + remainder + ending
            
    elif first in '/':
        # This is text : Don't do lots of extra stuff
        fixme = ''
        if 'IE' in content:
            fixme = " FIXME for IE-switches - may need an [endif] comment"
        print indent + "<!--" + content[1:]  + fixme + " -->"
        
    else:
        # This is text : Don't do lots of extra stuff
        print indent + content + ending


"""
matchObj = re.match( r'(.*) are(\.*)', line, re.M|re.I)

if matchObj:
   print "matchObj.group() : ", matchObj.group()
   print "matchObj.group(1) : ", matchObj.group(1)
   print "matchObj.group(2) : ", matchObj.group(2)
else:
   print "No match!!"
"""