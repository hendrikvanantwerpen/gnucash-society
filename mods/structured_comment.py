#!/usr/bin/env python

# Copyright (c) 2010-2011, Hendrik van Antwerpen
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

class StructuredComment:

    def __init__(self,comment):
        self.comment = comment
        self._parse()

    def _parse(self):
        self.struct = []
        lines = self.comment.split('\n')
        for line in lines:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                self.struct.append([key,value])
            elif len(line):
                self.struct.append(line)

    # get all varaibles in the comment as a map
    def get_entries(self):
        entries = {}
        for entry in self.struct:
            if not isinstance(entry, basestring):
                entries[entry[0]] = entry[1]
        return entries

    # get all the normal text, without the variables
    def get_text(self):
        text = ''
        for entry in self.struct:
            if isinstance(entry, basestring):
                text += entry+'\n'
        return text

    # get complete comment (text + variables)
    def get_comment(self):
        comment = ''
        for entry in self.struct:
            if isinstance(entry, basestring):
                comment += entry+'\n'
            else:
                comment += "%s: %s\n" % (entry[0],entry[1])
        return comment

    # set variable value, update if exists, otherwise add
    def set_entry(self,key,value):
        found = False
        for entry in self.struct:
            if not isinstance(entry, basestring) and entry[0] == key:
                entry[1] = value
                found = True
                break
        if not found:
            self.struct.append([key,value])

    # get variable value or None
    def get_entry(self,key):
        for entry in self.struct:
            if not isinstance(entry, basestring) and entry[0] == key:
                return entry[1]
        return None

    def get_string(self,key):
        s = self.get_entry(key)
        return ( s and str(s) ) or None

    def get_int(self,key):
        s = self.get_entry(key)
        return ( s and int(s) ) or None

    def get_bool(self,key):
        s = self.get_entry(key)
        return ( s and bool(s) ) or None

    def remove_entry(self,key):
        for entry in self.struct:
            if not isinstance(entry, basestring) and entry[0] == key:
                self.struct.remove(entry)

    # add text to the comment - not reparsed!
    def add_text(self,text):
        self.struct.append(text)
