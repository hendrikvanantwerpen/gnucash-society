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

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from mods import *

from gtkmods import *
from gtkmods.dialogs import *

from gnucash import Transaction, Split, GncLot

from gcmods import *
from gcmods.accounts import AccountReport
from gcmods.numeric import *


def new():
    return TaxesTab()

class TaxesTab:

    def init(self,app):
        self.app = app

        builder = gtk.Builder()
        builder.add_from_file(os.path.join(__dir__,'taxes.glade'))
        builder.connect_signals(self)

        self.tab = builder.get_object('main_tab')

        self.taxes_btw_hoog_label = builder.get_object('taxes_btw_hoog_label')
        self.taxes_btw_laag_label = builder.get_object('taxes_btw_laag_label')
        self.taxes_btw_import_label = builder.get_object('taxes_btw_import_label')
        self.taxes_voorbelasting_label = builder.get_object('taxes_voorbelasting_label')
        self.taxes_btw_eu_label = builder.get_object('taxes_btw_eu_label')
        self.taxes_btw_total_label = builder.get_object('taxes_btw_total_label')

        self.taxes_start_entry = builder.get_object('taxes_start_entry')
        self.taxes_end_entry = builder.get_object('taxes_end_entry')
        self.taxes_reportfile_entry = builder.get_object('taxes_reportfile_entry')
        d = date.today()
        d = d.replace(day=1)
        end = d - relativedelta(days=1)
        start = d - relativedelta(months=1)
        self.taxes_start_entry.set_text(start.strftime(self.app.DATE_FMT))
        self.taxes_end_entry.set_text(end.strftime(self.app.DATE_FMT))

    def get_name(self):
        return "Taxes"

    def get_component(self):
        return self.tab


    def refresh(self):
        self.taxes_btw_hoog_label.set_text('€ -')
        self.taxes_btw_laag_label.set_text('€ -')
        self.taxes_btw_import_label.set_text('€ -')
        self.taxes_voorbelasting_label.set_text('€ -')
        self.taxes_btw_total_label.set_text('€ -')
        self.taxes_btw_eu_label.set_text('€ -')

    def on_taxes_update(self,button):
        self.app.long_task(self._taxes_update_task)

    def _taxes_update_task(self):
        try:
            start = datetime.strptime(self.taxes_start_entry.get_text(),self.app.DATE_FMT).date()
            end = datetime.strptime(self.taxes_end_entry.get_text(),self.app.DATE_FMT).date()
        except:
            showErrorMessage("Start or end date is invalid. Expecting YYYY-MM-DD format.")
            return
        if end <= start:
            showErrorMessage("End date must be later then start date.")
            return

        tax_file = '%s-btwdeclaration-%s_%s.csv' % (
            date.today().strftime(self.app.DATE_FMT),
            start.strftime(self.app.DATE_FMT),
            end.strftime(self.app.DATE_FMT),
        )
        self.taxes_reportfile_entry.set_text(tax_file)

        self.taxes_total = GncNumeric()

        self.taxes_btw_collected_high = AccountReport(self.app.accounting.btw_collected_high,start,end,"BTW Hoog (19%)")
        self.taxes_total = self.taxes_total.add_fixed(self.taxes_btw_collected_high.report_total)
        self.taxes_btw_hoog_label.set_text('€ %g' % self.taxes_btw_collected_high.report_total.neg().to_double())

        self.taxes_btw_collected_low = AccountReport(self.app.accounting.btw_collected_low,start,end,"BTW Laag (6%)")
        self.taxes_total = self.taxes_total.add_fixed(self.taxes_btw_collected_low.report_total)
        self.taxes_btw_laag_label.set_text('€ %g' % self.taxes_btw_collected_low.report_total.neg().to_double())

        self.taxes_btw_import = AccountReport(self.app.accounting.btw_collected_import,start,end,"BTW Import")
        self.taxes_total = self.taxes_total.add_fixed(self.taxes_btw_import.report_total)
        self.taxes_btw_import_label.set_text('€ %g' % self.taxes_btw_import.report_total.neg().to_double())

        self.taxes_btw_paid_nl = AccountReport(self.app.accounting.btw_paid_nl,start,end,"Voorbelasting")
        self.taxes_total = self.taxes_total.add_fixed(self.taxes_btw_paid_nl.report_total)
        self.taxes_voorbelasting_label.set_text('€ %g' % self.taxes_btw_paid_nl.report_total.to_double())

        self.taxes_btw_total_label.set_text('€ %g' % self.taxes_total.to_double())

        self.taxes_btw_paid_eu = AccountReport(self.app.accounting.btw_paid_eu,start,end,"BTW uit EU-landen")
        self.taxes_btw_eu_label.set_text('€ %g' % self.taxes_btw_paid_eu.report_total.to_double())

    def on_taxes_create_transaction(self,button):
        self.app.long_task(self._taxes_create_transaction_task)

    def _taxes_create_transaction_task(self):
        today = date.today()
        tax_desc = "BTW Return %s - %s" % (
            self.taxes_btw_collected_high.startdate.strftime(self.app.DATE_FMT),
            self.taxes_btw_collected_high.enddate.strftime(self.app.DATE_FMT),
        )

        book = self.app.accounting.book
        txn = Transaction(book)
        txn.BeginEdit()
        txn.SetDate(today.day,today.month,today.year)
        txn.SetDescription(tax_desc)
        txn.SetCurrency(self.app.accounting.EUR)

        total = GncNumeric()
        rest = GncNumeric()

        def add_split(acct_taxes,acct_report,total,rest):
            s = Split(book)
            s.SetParent(txn)
            s.SetAccount(acct_report)
            s.SetValue(acct_taxes.total.neg())

            total = total.add_fixed(acct_taxes.report_total)
            rest = rest.add_fixed(acct_taxes.report_rest)

            return (total,rest)

        (total,rest) = add_split(self.taxes_btw_collected_high,self.app.accounting.btw_reported_high,total,rest)
        (total,rest) = add_split(self.taxes_btw_collected_low,self.app.accounting.btw_reported_low,total,rest)
        (total,rest) = add_split(self.taxes_btw_import,self.app.accounting.btw_reported_import,total,rest)
        (total,rest) = add_split(self.taxes_btw_paid_nl,self.app.accounting.btw_reported_nl,total,rest)

        # payment or receive
        if total.negative_p():
            result_account = self.app.accounting.payables
        else:
            result_account = self.app.accounting.receivables
        s = Split(book)
        s.SetParent(txn)
        s.SetAccount(result_account)
        s.SetValue(total)
        
        # payment / receive lot
        l = GncLot(book)
        result_account.InsertLot(l)
        l.begin_edit()
        l.add_split(s)
        l.set_title(tax_desc)
        l.commit_edit()

        # rounding differences in expense account
        s = Split(book)
        s.SetParent(txn)
        s.SetAccount(self.app.accounting.tax_expense)
        s.SetValue(txn.GetImbalanceValue().neg())

        txn.CommitEdit()

        self.app.accounting.save()

        self.app.set_status_text("%s transaction created." % tax_desc)

    def on_taxes_save_report(self,button):
        self.app.long_task(self._taxes_save_report_task)

    def _taxes_save_report_task(self):
        io_file = self.taxes_reportfile_entry.get_text()
        try:
            io = open(io_file,'w')
        except:
            showErrorMessage("Cannot open file: "+io_file)
            return
        try:
            self.taxes_btw_collected_high.write(io)
            self.taxes_btw_collected_low.write(io)
            self.taxes_btw_import.write(io)
            self.taxes_btw_paid_nl.write(io)
            self.taxes_btw_paid_eu.write(io)
            self.app.set_status_text("Tax Return report %s succesfully written." % io_file)
        except:
            showErrorMessage("Error generating %s." % io_file)
            io.write("""
            ###############################################
            # WARNING : An error occured when writing this
            # WARNING : file. It is most likely incomplete!
            ###############################################
            """)
            io.close()
        else:
            io.close()


    def on_taxreport_file_select(self,button):
        e = self.taxes_reportfile_entry
        f = showSaveDialog(title="Save Clieop03 File",filename=e.get_text())
        f and e.set_text(f)
