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
