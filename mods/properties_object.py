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
