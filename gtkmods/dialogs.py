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
