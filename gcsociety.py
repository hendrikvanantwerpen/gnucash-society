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
__dir__ = os.path.dirname(os.path.abspath(__file__))

import sys
import gobject
import gconf

GCONF_ROOT = '/apps/gcsociety/finances'

import gnucash_provider

from gcmods import *
from gcmods.accounting import Accounting
from gcmods.transactions import Unreconciled
from gcmods.contacts import Contacts

from gtkmods.dialogs import *

import tabs

class GCSocietyApp:       

    GNUCASH_KEY = GCONF_ROOT + '/gnucash_filename'
    WINDOW_W_KEY = GCONF_ROOT + '/window/width'
    WINDOW_H_KEY = GCONF_ROOT + '/window/height'
    ACCOUNTHOLDER_KEY = GCONF_ROOT + '/bank/accountholder'
    ACCOUNTNUMBER_KEY = GCONF_ROOT + '/bank/accountnumber'

    DATE_FMT = '%Y-%m-%d'

    accountholder = None
    accounting = None
    accountnumber = None
    vendors = None

    def __init__(self):
        self.init_conf()
        self.init_gui()
        self.init_tabs()
        self.gnucash_filename_changed()

    def init_conf(self):
        self.conf = gconf.client_get_default()
        self.conf.add_dir(GCONF_ROOT, gconf.CLIENT_PRELOAD_NONE)
        self.conf.notify_add(GCONF_ROOT, self.on_conf_change)

    def init_gui(self):
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(__dir__,'gcsociety.glade'))
        builder.connect_signals(self)

        self.window = builder.get_object('main_window')
        self.notebook = builder.get_object('notebook')
        self.statusbar = builder.get_object('statusbar')

        self.init_settings(builder)

        w = self.conf.get_int(GCSocietyApp.WINDOW_W_KEY)
        h = self.conf.get_int(GCSocietyApp.WINDOW_H_KEY)
        if w and h:
            self.window.resize(w,h)
        self.window.show()

    def init_tabs(self):
        self.tabs = [ tabs.members.new(), tabs.invoices.new(), tabs.taxes.new(), tabs.banking.new() ]
        for tab in self.tabs:
            tab.init(self)
            self.notebook.prepend_page(tab.get_component(), gtk.Label(tab.get_name()))
        self.notebook.set_current_page(0)

    def refresh(self):
        for tab in self.tabs:
            tab.refresh()
    
    ####################
    # Settings functions
    ####################

    def init_settings(self,builder):
        gff = builder.get_object('gnucash_filefilter')
        gff.set_name("GnuCash Files (*.gnucash)")
        gff.add_pattern('*.gnucash')

        filename = self.conf.get_string(GCSocietyApp.GNUCASH_KEY)
        gnucash_filechooser = builder.get_object('gnucash_filechooser')
        self.gnucash_filename = showOpenDialog(title="Open GnuCash file", filter='*.gnucash', filename=filename) or ''
        gnucash_filechooser.set_filename(self.gnucash_filename)

        self.accountholder = self.conf.get_string(GCSocietyApp.ACCOUNTHOLDER_KEY)
        ahe = builder.get_object('bank_accountholder_entry')
        ahe.set_text(self.accountholder or '')

        self.accountnumber = self.conf.get_int(GCSocietyApp.ACCOUNTNUMBER_KEY)
        ane = builder.get_object('bank_accountnumber_entry')
        ane.set_text( ( self.accountnumber and str(self.accountnumber) ) or '')

    def gnucash_filename_changed(self):
        self.accounting = None
        self.payables = None
        self.receivables = None
        if self.gnucash_filename:
            self.set_status_text("Using %s" %
                    os.path.basename(self.gnucash_filename))
            try:
                self.accounting = Accounting(self.gnucash_filename)
            except Exception as ex:
                showErrorMessage("Cannot load %s: %s" % (self.gnucash_filename,ex))
                self.gnucash_filename = None
                self.accounting = None
            else:
                self.payables = Unreconciled(self.accounting,
                        Unreconciled.Type.PAYABLES)
                self.receivables = Unreconciled(self.accounting,
                        Unreconciled.Type.RECEIVABLES)
        else:
            self.set_status_text("No GnuCash file selected. Go to settings to fix this.")
        self.update_contacts()
        self.refresh()

    def update_contacts(self):
        if self.accounting:
            contacts = Contacts(self.accounting)
            self.customers = contacts.get_customers()
            self.vendors = contacts.get_vendors()
        else:
            self.customers = []
            self.vendors = []

    def on_gnucash_file_set(self,fc):
        self.conf.set_string(GCSocietyApp.GNUCASH_KEY,fc.get_filename())

    def on_bank_accountholder_changed(self,entry):
        self.conf.set_string(GCSocietyApp.ACCOUNTHOLDER_KEY,entry.get_text())

    def on_bank_accountnumber_changed(self,entry):
        try:
            num = int(entry.get_text())
            self.conf.set_int(GCSocietyApp.ACCOUNTNUMBER_KEY,num)
        except:
            entry.set_text('')

    def on_conf_change(self, conf, timestamp, entry, *extra):
        key = entry.get_key()
        value = entry.get_value()
        if key == GCSocietyApp.GNUCASH_KEY:
            self.gnucash_filename = value.get_string()
            self.gnucash_filename_changed()
        elif key == GCSocietyApp.ACCOUNTHOLDER_KEY:
            self.accountholder = value.get_string()
        elif key == GCSocietyApp.ACCOUNTNUMBER_KEY:
            self.accountnumber = value.get_int()
        else:
            print 'unhandled conf change %s -> %s' % (key,value)

    ####################################
    # Window and configuration functions
    ####################################

    def long_task(self,func,*args):
        def idle_cb(gtk_window):
            try:
                func(*args)
            except:
                gtk_window.set_cursor(None)
                raise
            else:
                gtk_window.set_cursor(None)
        watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
        gtk_window = self.window.get_property('window')
        gtk_window.set_cursor(watch)
        gobject.idle_add(idle_cb, gtk_window)

    def on_window_destroy(self,evt):
        size = self.window.allocation
        self.conf.set_int(GCSocietyApp.WINDOW_W_KEY,size.width)
        self.conf.set_int(GCSocietyApp.WINDOW_H_KEY,size.height)
        if self.accounting:
            self.accounting.session.end()
        gtk.main_quit()

    def set_status_text(self,text):
        cid = self.statusbar.get_context_id('default')
        self.statusbar.push(cid,text)

if __name__ == '__main__':
    app = GCSocietyApp()
    gtk.main()
