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
import sys

import gtk
import gconf

GNUCASH_KEY = '/apps/gnucash/moduledir'

prevpath = sys.path
conf = gconf.client_get_default()
gcpath = conf.get_string(GNUCASH_KEY)
if gcpath:
    sys.path.append(gcpath)
try:
    import gnucash
except ImportError:
    sys.path = prevpath
    dlg = gtk.FileChooserDialog(
        title="Select gnucash.py",
        parent=None,
        action=gtk.FILE_CHOOSER_ACTION_OPEN,
        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK)
    )
    f = gtk.FileFilter()
    f.set_name("GnuCash Python Module (gnucash.py)")
    def gcfilter(fi):
        filename = fi[0]
        return os.path.isdir(filename) or filename.endswith(os.path.join('gnucash','__init__.py'))
    f.add_custom(gtk.FILE_FILTER_FILENAME,gcfilter)
    dlg.set_filter(f)
    ret = dlg.run()
    dlg.hide()
    if ret == gtk.RESPONSE_OK:
        filename = dlg.get_filename()
        filename = filename.replace(os.path.join('gnucash','__init__.py'),'')
        sys.path.append(filename)
        conf.set_string(GNUCASH_KEY,filename)
    else:
        sys.exit(-1)
    dlg.destroy()
