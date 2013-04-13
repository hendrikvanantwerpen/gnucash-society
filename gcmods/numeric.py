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

from gnucash import GncNumeric, GNC_HOW_RND_ROUND
from gnucash._gnucash_core_c import double_to_gnc_numeric, string_to_gnc_numeric

DENOM = 100

def gncn_round_with_rest(n):
    sign = 1
    if ( n.negative_p() ):
        n = n.neg()
        sign = -1

    thres = int(n.denom() / 2)
    num = n.num() + thres
    rest = num % n.denom()
    num = num - rest
    rest = rest - thres

    return (GncNumeric(sign*num,n.denom()),GncNumeric(sign*rest,n.denom()))

def gncn_floor_with_rest(n):
    sign = 1
    if ( n.negative_p() ):
        n = n.neg()
        sign = -1

    rest = n.num() % n.denom()
    return (GncNumeric(sign*(n.num()-rest),n.denom()),GncNumeric(sign*rest,n.denom()))

def gncn_from_string(s):
    return gncn_from_double(float(s))

def gncn_from_int(i):
    return GncNumeric(i*DENOM,DENOM)

def gncn_from_double(d):
    return GncNumeric(round(d*DENOM),DENOM)
