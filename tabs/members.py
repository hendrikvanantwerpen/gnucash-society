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
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

import gobject
import gtk
import pygtk
import gconf

from mods import *
from mods.structured_comment import StructuredComment
from mods.enum import enum
from mods.id_factory import IdFactory

from gtkmods import *
from gtkmods.dialogs import *

from gnucash import Transaction, Split, GncNumeric, GncLot
from gnucash.gnucash_business import GNC_AMT_TYPE_PERCENT, Invoice, Entry

from gcmods import *
from gcmods.accounting import Accounting
from gcmods.transactions import Unreconciled
from gcmods.contacts import Contacts, ContactsSync
from gcmods.accounts import AccountReport
from gcmods.numeric import *

MembersFieldCols = enum('FIELD')

def new():
    return MembersTab()

class MembersTab:       

    def init(self,app):
        self.app = app

        builder = gtk.Builder()
        builder.add_from_file(os.path.join(__dir__,'members.glade'))
        builder.connect_signals(self)

        self.tab = builder.get_object('main_tab')

        gff = builder.get_object('csv_filefilter')
        gff.set_name("CiviCRM Export Files (*.csv)")
        gff.add_pattern('*.csv')

        self.members_field_model = builder.get_object('members_field_model')
        self.members_id_combo = builder.get_object('members_id_combo')
        self.members_name_combo = builder.get_object('members_name_combo')
        self.members_accountholder_combo = builder.get_object('members_accountholder_combo')
        self.members_accountnumber_combo = builder.get_object('members_accountnumber_combo')
        self.members_incasso_combo = builder.get_object('members_incasso_combo')

    def get_name(self):
        return "Members"

    def get_component(self):
        return self.tab

    def refresh(self):
        pass

    def on_members_file_set(self,fc):
        filename = fc.get_filename()
        self.members_field_model.clear()
        if not filename:
            return
        self.members_sync = ContactsSync(self.app.accounting,filename)
        for fieldname in self.members_sync.get_headers():
            self.members_field_model.append((fieldname,))

    def on_members_import(self,button):
        self.app.long_task(self._members_import_task)

    def _members_import_task(self):
        if not self.app.accounting:
            showErrorMessage("Select GnuCash file first.")
            return

        if not self.members_sync:
            showErrorMessage("Select CiviCRM export file first.")
            return

        self.members_sync.set_mapping('id', self.members_id_combo.get_active_text())
        self.members_sync.set_mapping('name', self.members_name_combo.get_active_text())
        self.members_sync.set_mapping('accountholder', self.members_accountholder_combo.get_active_text())
        self.members_sync.set_mapping('accountnumber', self.members_accountnumber_combo.get_active_text())
        self.members_sync.set_mapping('allowincasso', self.members_incasso_combo.get_active_text())

        self.members_sync.sync()

        self.app.set_status_text("Contacts synchronized.")
