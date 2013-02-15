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
