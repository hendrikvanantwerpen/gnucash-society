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

InvoicesLinesCols = enum('TAX','DESCRIPTION','AMOUNT','PRICE',
        'SUBTOTAL','TAXNAME','TAXINCL','ACCOUNTNAME','ACCOUNT')
InvoicesCustomersCols = enum('CONTACT','INCLUDE','NAME','INVOICEID')
InvoicesTaxesCols = enum('TAX','DESCRIPTION')
InvoicesAccountsCols = enum('ACCOUNT','NAME')

def new():
    return InvoicesTab()

class InvoicesTab:       

    def init(self,app):
        self.app = app

        builder = gtk.Builder()
        builder.add_from_file(os.path.join(__dir__,'invoices.glade'))
        builder.connect_signals(self)

        self.tab = builder.get_object('main_tab')

        self.invoices_baseid_entry = builder.get_object('invoices_baseid_entry')
        self.invoices_startno_entry = builder.get_object('invoices_startno_entry')
        self.invoices_date = builder.get_object('invoices_date')
        self.invoices_notes_text = builder.get_object('invoices_notes_text')
        self.invoices_baseid_entry = builder.get_object('invoices_baseid_entry')
        self.invoices_description = builder.get_object('invoices_description')

        self.invoices_customers_model = builder.get_object('invoices_customers_model')
        self.invoices_lines_model = builder.get_object('invoices_lines_model')
        self.invoices_lines_model.append()
        self.invoices_taxes_model = builder.get_object('invoices_taxes_model')
        self.invoices_accounts_model = builder.get_object('invoices_accounts_model')
        self.invoices_customers_selector = builder.get_object('invoices_customers_selector')
        self.invoices_customers_list = builder.get_object('invoices_customers_list')

        self.invoices_baseid_entry.set_text("MyInvoice")
        self.invoices_startno_entry.set_text("1")
        self.invoices_date.set_text(date.today().strftime(self.app.DATE_FMT))

    def get_name(self):
        return "Mass Invoice"

    def get_component(self):
        return self.tab

    def refresh(self):
        self.refresh_invoices_accounts()
        self.refresh_invoices_taxes()
        self.refresh_invoices_customers()

    def refresh_invoices_accounts(self):
        self.invoices_accounts_model.clear()
        if self.app.accounting:
            for account in self.app.accounting.book.get_root_account().get_descendants_sorted():
                self.invoices_accounts_model.append((
                    account,
                    account.get_full_name(),
                ))

    def refresh_invoices_taxes(self):
        self.invoices_taxes_model.clear()
        if self.app.accounting:
            for tax in self.app.accounting.taxtables:
                self.invoices_taxes_model.append((
                    tax,
                    tax.GetName(),
                ))

    def on_invoices_line_desc_changed(self, cellrenderertext, path, new_text):
        row = self.invoices_lines_model[path]
        row[InvoicesLinesCols.DESCRIPTION] = new_text
        self._update_invoice(row)

    def on_invoices_line_amount_changed(self, cellrenderertext, path, new_text):
        row = self.invoices_lines_model[path]
        row[InvoicesLinesCols.AMOUNT] = int(new_text)
        self._update_invoice(row)

    def on_invoices_line_price_changed(self, cellrenderertext, path, new_text):
        row = self.invoices_lines_model[path]
        row[InvoicesLinesCols.PRICE] = float(new_text)
        self._update_invoice(row)

    def on_invoices_line_tax_changed(self,combo, path, new_iter):
        row = self.invoices_lines_model[path]
        tax = self.invoices_taxes_model[new_iter][InvoicesTaxesCols.TAX]
        row[InvoicesLinesCols.TAX] = tax
        row[InvoicesLinesCols.TAXNAME] = tax.GetName()
        self._update_invoice(row)

    def on_invoices_line_taxincl_changed(self, toggle, path):
        row = self.invoices_lines_model[path]
        row[InvoicesLinesCols.TAXINCL] = not toggle.get_active()
        self._update_invoice(row)

    def on_invoices_lines_key_event(self,lines_list,event):
        if gtk.gdk.keyval_name(event.keyval) == "Delete":
            iter = lines_list.get_selection().get_selected()[1]
            last = not lines_list.get_model().iter_next(iter)
            lines_list.get_model().remove(iter)
            if last or not lines_list.get_model().get_iter_first():
                lines_list.get_model().append()
            self._update_invoice(None)
            return True
        else:
            return False
        
    def _update_invoice(self,row):
        if row:
            amount = row[InvoicesLinesCols.AMOUNT]
            price = row[InvoicesLinesCols.PRICE]
            row[InvoicesLinesCols.SUBTOTAL] = round(100*amount*price)/100
            if not self.invoices_lines_model.iter_next(row.iter):
                self.invoices_lines_model.append()

    def refresh_invoices_customers(self):
        self.invoices_customers_model.clear()
        if self.app.customers:
            contacts = sorted(self.app.customers,key=lambda x: x['name'])
            for contact in contacts:
                self.invoices_customers_model.append((
                    contact,
                    False,
                    contact['name'],
                    ''
                ))

    def on_invoices_customers_selectall(self,header):
        sel = not self.invoices_customers_selector.get_active()
        self.invoices_customers_selector.set_active(sel)
        for row in self.invoices_customers_model:
            row[InvoicesCustomersCols.INCLUDE] = sel
        self._update_ids()

    def on_invoices_customer_select(self,tb,path):
        try:
            path = self.invoices_customers_list.get_model().convert_path_to_child_path(path)
        except:
            pass # not a filter
        model = self.invoices_customers_model
        self.invoices_customers_selector.set_active(False)
        row = model[path]
        row[InvoicesCustomersCols.INCLUDE] = not row[InvoicesCustomersCols.INCLUDE]
        self._update_ids()

    def on_id_change(self,*args):
        self._update_ids()

    def _update_ids(self):
        base = self.invoices_baseid_entry.get_text()
        try:
            start = int(self.invoices_startno_entry.get_text())
        except:
            showErrorMessage("Start number is not a number.")
            return
        idf = IdFactory(base,start)
        for row in self.invoices_customers_model:
            if row[InvoicesCustomersCols.INCLUDE]:
                row[InvoicesCustomersCols.INVOICEID] = idf.getId()
            else:
                row[InvoicesCustomersCols.INVOICEID] = ''

    def on_invoices_customers_filter(self,toggle):
        if toggle.get_active():
            f = self.invoices_customers_model.filter_new()
            def include_filter(model, iter):
                return model[iter][InvoicesCustomersCols.INCLUDE]
            f.set_visible_func(include_filter)
            self.invoices_customers_list.set_model(f)
        else:
            self.invoices_customers_list.set_model(self.invoices_customers_model)

    def on_invoice_line_account_changed(self,combo, path, new_iter):
        row = self.invoices_lines_model[path]
        account = self.invoices_accounts_model[new_iter][InvoicesAccountsCols.ACCOUNT]
        row[InvoicesLinesCols.ACCOUNT] = account
        row[InvoicesLinesCols.ACCOUNTNAME] = account.get_full_name()
        self._update_invoice(row)

    def on_invoices_generate(self,button):
        self.app.long_task(self._invoices_generate_task)

    def _invoices_generate_task(self):
        try:
            idate = datetime.strptime(self.invoices_date.get_text(),self.app.DATE_FMT).date()
        except:
            showErrorMessage("Date is invalid.")
            return
        description = self.invoices_description.get_text()
        notes = self.invoices_notes_text.get_buffer().get_property('text')
        if not description:
            showErrorMessage("No description for the invoice.")
            return
        if len(self.invoices_lines_model) <= 1:
            showErrorMessage("No lines for the invoice.")
            return
        for erow in self.invoices_lines_model:
            last = not self.invoices_lines_model.iter_next(erow.iter)
            if last:
                break
            if not erow[InvoicesLinesCols.DESCRIPTION]:
                showErrorMessage("Not all lines have a description.")
                return
            if not erow[InvoicesLinesCols.AMOUNT]:
                showErrorMessage("Not all lines have an amount set.")
                return
            if not erow[InvoicesLinesCols.ACCOUNT]:
                showErrorMessage("Not all lines have an account set.")
                return
            if not erow[InvoicesLinesCols.PRICE]:
                showErrorMessage("Not all lines have a price set.")
                return
            if not erow[InvoicesLinesCols.TAX]:
                if not showQuestion("Not all lines have taxes specified. Continue anyway?"):
                    return

        book = self.app.accounting.book
        EUR = self.app.accounting.EUR
        has_any = False
        for crow in self.invoices_customers_model:
            if not crow[InvoicesCustomersCols.INCLUDE]:
                continue
            has_any = True
            invoice = Invoice(book,
                crow[InvoicesCustomersCols.INVOICEID],
                EUR,
                crow[InvoicesCustomersCols.CONTACT].owner,
                idate
            )
            invoice.SetNotes(notes)
            for erow in self.invoices_lines_model:
                last = not self.invoices_lines_model.iter_next(erow.iter)
                if last:
                    break
                invoice_entry = Entry(book, invoice)
                tax = erow[InvoicesLinesCols.TAX]
                if tax:
                    invoice_entry.SetInvTaxTable(tax)
                    invoice_entry.SetInvTaxIncluded(True)
                invoice_entry.SetDescription( erow[InvoicesLinesCols.DESCRIPTION] )
                invoice_entry.SetQuantity( GncNumeric( erow[InvoicesLinesCols.AMOUNT] ) )
                invoice_entry.SetInvAccount( erow[InvoicesLinesCols.ACCOUNT] )
                invoice_entry.SetInvPrice( gncn_from_double( erow[InvoicesLinesCols.PRICE] ) )
            invoice.PostToAccount(self.app.accounting.receivables, idate, idate, description, True)
        if not has_any:
            showInfoMessage("No customers were selected. Mistake?")
        else:
            self.app.accounting.save()
            self.app.set_status_text("Invoices are created.")
