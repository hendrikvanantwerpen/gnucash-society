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
import gobject
import gtk

from conf import Conf
from gcmods import *
from gcmods.accounting import Accounting
from gcmods.transactions import Unreconciled
from gcmods.contacts import Contacts

from gtkmods.dialogs import *

import tabs

class GCSocietyApp:

    CONF_ROOT = '/apps/gcsociety'
    WINDOW_W_KEY = '/window/width'
    WINDOW_H_KEY = '/window/height'
    ACCOUNTHOLDER_KEY = '/bank/accountholder'
    ACCOUNTNUMBER_KEY = '/bank/accountnumber'

    DATE_FMT = '%Y-%m-%d'

    accountholder = None
    accounting = None
    accountnumber = None

    def __init__(self,conf,filename):
        self.app_conf = conf
        self.file_conf = conf.get_child('/'+self.key_from_filename(filename))
        self.gnucash_filename = filename
        self.init_gui()
        self.init_tabs()
        self.init_gnucash()

    def key_from_filename(self,filename):
        return filename.replace('/','-').replace('\\','-').replace(' ','_')

    def init_gui(self):
        builder = gtk.Builder()
        builder.add_from_file(os.path.join(__dir__,'gcsociety.glade'))
        builder.connect_signals(self)

        self.window = builder.get_object('main_window')
        self.notebook = builder.get_object('notebook')
        self.statusbar = builder.get_object('statusbar')

        self.init_settings(builder)

        w = self.app_conf.get_int(GCSocietyApp.WINDOW_W_KEY)
        h = self.app_conf.get_int(GCSocietyApp.WINDOW_H_KEY)
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
        self.file_conf.on_add(self.on_settings_change)

        self.accountholder = self.file_conf.get_string(GCSocietyApp.ACCOUNTHOLDER_KEY)
        ahe = builder.get_object('bank_accountholder_entry')
        ahe.set_text(self.accountholder or '')

        self.accountnumber = self.file_conf.get_int(GCSocietyApp.ACCOUNTNUMBER_KEY)
        ane = builder.get_object('bank_accountnumber_entry')
        ane.set_text( ( self.accountnumber and str(self.accountnumber) ) or '')

    def on_bank_accountholder_changed(self,entry):
        self.file_conf.set_string(GCSocietyApp.ACCOUNTHOLDER_KEY,entry.get_text())

    def on_bank_accountnumber_changed(self,entry):
        try:
            num = int(entry.get_text())
            self.file_conf.set_int(GCSocietyApp.ACCOUNTNUMBER_KEY,num)
        except:
            entry.set_text('')

    def on_settings_change(self, key, value):
        if key == GCSocietyApp.ACCOUNTHOLDER_KEY:
            self.accountholder = value.get_string()
        elif key == GCSocietyApp.ACCOUNTNUMBER_KEY:
            self.accountnumber = value.get_int()
        else:
            print 'unhandled conf change %s -> %s' % (key,value)

    ##############
    # Open GnuCash 
    ##############

    def init_gnucash(self):
        self.accounting = None
        self.payables = None
        self.receivables = None
        self.set_status_text("Using %s" %
                os.path.basename(self.gnucash_filename))
        try:
            self.accounting = Accounting(self.gnucash_filename)
        except Exception as ex:
            showErrorMessage("Cannot load %s: %s" % (self.gnucash_filename,ex))
            self.window.destroy()
        else:
            self.payables = Unreconciled(self.accounting,
                    Unreconciled.Type.PAYABLES)
            self.receivables = Unreconciled(self.accounting,
                    Unreconciled.Type.RECEIVABLES)
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
        self.app_conf.set_int(GCSocietyApp.WINDOW_W_KEY,size.width)
        self.app_conf.set_int(GCSocietyApp.WINDOW_H_KEY,size.height)
        if self.accounting:
            self.accounting.session.end()
        gtk.main_quit()

    def set_status_text(self,text):
        cid = self.statusbar.get_context_id('default')
        self.statusbar.push(cid,text)
