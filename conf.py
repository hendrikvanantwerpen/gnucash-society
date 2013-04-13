#!/usr/bin/env python
# coding=UTF-8

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

import os
__dir__ = os.path.dirname(os.path.abspath(__file__))

import gconf

class Conf:

    def __init__(self,root):
        self.root = root
        self.conf = gconf.client_get_default()
        self.conf.add_dir(root, gconf.CLIENT_PRELOAD_NONE)

    def get_child(self,key):
        return Conf(self.root+key)

    def on_add(self,handler):
        def _h(conf,timestamp,entry,*extra):
            key = entry.get_key()[len(self.root):]
            val = entry.get_value()
            handler(key,val)
        self.conf.notify_add(self.root,_h)

    def get_int(self,key):
        return self.conf.get_int(self.root+key)

    def set_int(self,key,val):
        return self.conf.set_int(self.root+key,val)

    def get_string(self,key):
        return self.conf.get_string(self.root+key)

    def set_string(self,key,val):
        return self.conf.set_string(self.root+key,val)
