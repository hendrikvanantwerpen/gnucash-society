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

import gtk

def showErrorMessage(msg):
    b = gtk.MessageDialog(
        flags=gtk.DIALOG_MODAL,
        type=gtk.MESSAGE_ERROR,
        buttons=gtk.BUTTONS_CLOSE,
        message_format=msg,
    )
    b.run()
    b.destroy()

def showInfoMessage(msg):
    b = gtk.MessageDialog(
        flags=gtk.DIALOG_MODAL,
        type=gtk.MESSAGE_INFO,
        buttons=gtk.BUTTONS_CLOSE,
        message_format=msg,
    )
    b.run()
    b.destroy()

def showQuestion(msg):
    b = gtk.MessageDialog(
        flags=gtk.DIALOG_MODAL,
        type=gtk.MESSAGE_INFO,
        buttons=gtk.BUTTONS_YES_NO,
        message_format=msg,
    )
    ret = b.run()
    b.destroy()
    return ret == gtk.RESPONSE_YES

def showSaveDialog(title="Save file", filter="*.*", filename=None):
    dlg = gtk.FileChooserDialog(title=title, parent=None, action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    filename and dlg.set_current_name(filename)
    if dlg.run() == gtk.RESPONSE_OK:
        ret = dlg.get_filename()
    else:
        ret = None
    dlg.destroy()
    return ret

def showOpenDialog(title="Open file", filter="*.*", filename=None):
    dlg = gtk.FileChooserDialog(title=title, parent=None, action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    filename and dlg.set_current_name(filename)
    if dlg.run() == gtk.RESPONSE_OK:
        ret = dlg.get_filename()
    else:
        ret = None
    dlg.destroy()
    return ret
