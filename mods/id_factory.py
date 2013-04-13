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

class IdFactory:

    def __init__(self,base='',start=0,num=3):
        self.curr = start
        self.ptrn = "%s%%0%dd" % (base,num)

    def getId(self):
        id = self.ptrn % self.curr
        self.curr += 1
        return id
