#!/usr/bin/env python

# Copyright 2010-2013 Hendrik van Antwerpen
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
