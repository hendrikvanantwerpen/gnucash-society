#!/usr/bin/env python
# coding=UTF-8

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
