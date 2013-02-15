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

class PropertiesObject:

    def __init__(self,definition=[],initial=None):
        if isinstance(definition,dict):
            self.properties = definition 
        else:
            self.properties = {}
            for key in definition:
                self.properties[key] = None
        self.__initialized = True
        if initial:
            for key in initial:
                self[key] = initial[key]

    def __len__(self):
        return self.properties.__len__()

    def __contains__(self,item):
        return self.properties.__contains__(item)

    def __iter__(self):
        return self.properties.__iter__()

    def keys(self):
        return self.properties.keys()

    def __getitem__(self,key):
        return self.properties.__getitem__(key)

    def __getattr__(self,name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setitem__(self,key,value):
        if not self.__dict__.has_key('_PropertiesObject__initialized'):
            self.__dict__[key] = value
        elif self.properties.has_key(key):
            self.properties[key] = value
        else:
            raise KeyError(key)

    def __setattr__(self,name,value):
        if self.__dict__.has_key(name):
            self.__dict__[name] = value
        else:
            try:
                self[name] = value
            except KeyError:
                raise AttributeError(name)

    def __repr__(self):
        return self.properties.__repr__()

def test_properties_object():
    po = PropertiesObject({'name':None,'value':42,'array':[]})
    print po
    po = PropertiesObject(['name','value'],{'name':None,'value':42})
    print po
    print po.name
    for p in po:
        print "%s: %s" % (p,po[p])
    po.name = "aap"
    print po
    po.waarde = 43
#test_properties_object()
