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

import sys
from conf import Conf
from gtkmods.dialogs import *

import gnucash_provider
from gcsociety import GCSocietyApp

GNUCASH_KEY = '/gnucash_filename'

def get_gnucash_filename(conf):
    filename = None
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = conf.get_string(GNUCASH_KEY)
        filename = showOpenDialog(title="Open GnuCash file", filter='*.gnucash', filename=filename) or None
    return filename

if __name__ == '__main__':
    conf = Conf(GCSocietyApp.CONF_ROOT)
    filename = get_gnucash_filename(conf)
    if filename != None:
        GCSocietyApp(conf,os.path.abspath(filename))
        gtk.main()
    else:
        showErrorMessage('You must choose a GnuCash file. Exiting.')
