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

from datetime import date, datetime

from gcsociety import GCSocietyApp

from mods import *
from mods.enum import enum

from gtkmods import *
from gtkmods.dialogs import *

from gcmods import *
from gcmods.numeric import *

BankingModesCols = enum('MODE')
BankingContactsCols = enum('CONTACT','NAME')
BankingTransactionsCols = enum('TRANSACTION','CONTACT','INCLUDE',
        'INVOICEID','DESCRIPTION','AMOUNT','CONTACTNAME',
        'ACCOUNTHOLDER','ACCOUNTNUMBER','ALLOWINCASSO')

def new():
    return BankingTab()

class BankingTab:       

    banking_contacts = None
    transactions = None

    def init(self,app):
        self.app = app

        builder = gtk.Builder()
        builder.add_from_file(os.path.join(__dir__,'banking.glade'))
        builder.connect_signals(self)

        self.tab = builder.get_object('main_tab')

        self.banking_mode = builder.get_object('banking_mode_combo').get_active_text()
        self.banking_transactions_view = builder.get_object('banking_transactions_view')
        col = self.banking_transactions_view.get_column(BankingTransactionsCols.INCLUDE)
        def disable_illegal_incasso(column, cell, model, iter):
            cell.set_property('sensitive', self.block_inclusion(
                    model.get_value(iter,BankingTransactionsCols.ALLOWINCASSO)
            ))
        col.set_cell_data_func(col.get_cell_renderers()[0],
                disable_illegal_incasso)
        self.banking_transactions_selector = builder.get_object('banking_transactions_selector')
        self.banking_transactions_model = builder.get_object('banking_transactions_model')

        self.banking_contacts_model = builder.get_object('banking_contacts_model')

        self.banking_clieopfile_entry = builder.get_object('banking_clieopfile_entry')
        self.clieop_date_entry = builder.get_object('clieop_date_entry')
        self.clieop_date_entry.set_text(date.today().strftime(self.app.DATE_FMT))

    def get_name(self):
        return "Banking"

    def get_component(self):
        return self.tab

    def refresh(self):
        if self.app.accounting:
            if self.banking_mode == 'Payables':
                self.transactions = self.app.payables
                self.banking_contacts = self.app.vendors
                self.block_inclusion = lambda x: True
            elif self.banking_mode == 'Receivables':
                self.transactions = self.app.receivables
                self.banking_contacts = self.app.customers
                self.block_inclusion = lambda x: x
        self.refresh_banking_contacts()
        self.refresh_banking_transactions()

    def refresh_banking_contacts(self):
        self.banking_contacts_model.clear()
        if self.banking_contacts:
            contacts = sorted(self.banking_contacts,key=lambda x: x['name'])
            for contact in contacts:
                self.banking_contacts_model.append((
                    contact,
                    contact['name'],
                ))

    def refresh_banking_transactions(self):
        self.banking_transactions_model.clear()
        if self.transactions:
            for txn in self.transactions.get():
                self.banking_transactions_model.append((
                    txn,
                    txn.owner,
                    False,
                    txn.invoiceid or '',
                    txn.description or '',
                    txn.amount or 0,
                    (txn.owner and txn.owner.name) or '',
                    txn.accountholder or (txn.owner and txn.owner.accountholder) or '',
                    txn.accountnumber or (txn.owner and txn.owner.accountnumber) or 0,
                    txn.allowincasso or (txn.owner and txn.owner.allowincasso) or False,
                ))

    def on_banking_mode_change(self,cb):
        self.app.long_task(self._banking_mode_change_task,cb.get_active_text())

    def _banking_mode_change_task(self,mode):
            self.banking_transactions_selector.set_active(False)
            self.banking_mode = mode
            if self.banking_mode == 'Payables':
                self.banking_clieopfile_entry.set_text(
                    "%s-payments.clieop03" % datetime.today().strftime(self.app.DATE_FMT)
                )
            elif self.banking_mode == 'Receivables':
                self.banking_clieopfile_entry.set_text(
                    "%s-incassos.clieop03" % datetime.today().strftime(self.app.DATE_FMT)
                )
            self.refresh()

    def on_banking_select_all_toggled(self,checkbutton):
        sel = not self.banking_transactions_selector.get_active()
        self.banking_transactions_selector.set_active(sel)
        for row in self.banking_transactions_model:
            if self.block_inclusion(row[BankingTransactionsCols.ALLOWINCASSO]):
                row[BankingTransactionsCols.INCLUDE] = sel

    def on_banking_transaction_include_toggle(self,tb,row):
        self.banking_transactions_selector.set_active(False)
        txn = self.banking_transactions_model[row]
        if self.block_inclusion(txn[BankingTransactionsCols.ALLOWINCASSO]):
            txn[BankingTransactionsCols.INCLUDE] = not txn[BankingTransactionsCols.INCLUDE]

    def on_banking_contact_edit_start(self,cellrenderer,celleditable,path):
        completion = gtk.EntryCompletion()
        completion.set_model(self.banking_contacts_model)
        completion.set_text_column(BankingContactsCols.NAME)
        completion.connect('match-selected',self.on_banking_contact_selected,path)
        celleditable.set_completion(completion)
        hid = {}
        hid['hid'] = cellrenderer.connect('edited',self.on_banking_contact_edited,hid)

    def on_banking_contact_selected(self,completion,model,new_iter,path):
        contact = model.get_value(new_iter,BankingContactsCols.CONTACT)
        if contact:
            row = self.banking_transactions_model[path]
            row[BankingTransactionsCols.CONTACT] = contact
            row[BankingTransactionsCols.CONTACTNAME] = (contact and contact['name']) or ''
            row[BankingTransactionsCols.ACCOUNTHOLDER] = (contact and contact['accountholder']) or ''
            row[BankingTransactionsCols.ACCOUNTNUMBER] = (contact and contact['accountnumber']) or 0
            row[BankingTransactionsCols.ALLOWINCASSO] = (contact and contact['allowincasso']) or False

    def on_banking_contact_edited(self,cellrenderer,path,new_text,hid):
        cellrenderer.disconnect(hid['hid'])
        if not len(new_text):
            row = self.banking_transactions_model[path]
            row[BankingTransactionsCols.CONTACT] = None
            row[BankingTransactionsCols.ACCOUNTHOLDER] = row[BankingTransactionsCols.TRANSACTION].accountholder
            row[BankingTransactionsCols.ACCOUNTNUMBER] = row[BankingTransactionsCols.TRANSACTION].accountnumber
            row[BankingTransactionsCols.ALLOWINCASSO] = row[BankingTransactionsCols.TRANSACTION].allowincasso

    def on_banking_accountholder_changed(self,cellrenderertext,path,new_text):
        txn = self.banking_transactions_model[path]
        txn[BankingTransactionsCols.ACCOUNTHOLDER] = new_text

    def on_banking_accountnumber_changed(self,cellrenderertext,path,new_text):
        txn = self.banking_transactions_model[path]
        txn[BankingTransactionsCols.ACCOUNTNUMBER] = int(new_text)


    def on_banking_generate(self,button):
        self.app.long_task(self._banking_generate_task)

    def _banking_generate_task(self):
        io_file = self.banking_clieopfile_entry.get_text()
        try:
            io = open(io_file,'w')
        except:
            showErrorMessage("Cannot open Clieop file: "+io_file)
            return

        bestand = clieop03.Bestand()
        batch = clieop03.Batch()
        if self.banking_mode == 'Payables':
            batch.transactieGroep = clieop03.Batch.ZAKELIJKE_BETALINGEN
        elif self.banking_mode == 'Receivables':
            batch.transactieGroep = clieop03.Batch.INCASSO_OPDRACHTEN
        else:
            return
        batch.naamOpdrachtgever = self.app.accountholder
        batch.rekeningnummerOpdrachtgever = self.app.accountnumber
        batch.productie = True
        try:
            exec_date = datetime.strptime(self.clieop_date_entry.get_text(),self.app.DATE_FMT).date()
            if exec_date < date.today():
                showErrorMessage("Date "+exec_date.strftime(self.app.DATE_FMT)+" is in the past. Must be >= today.")
                return
            batch.gewensteVerwerkingsDatum = exec_date
        except:
            showErrorMessage("Invalid date: "+self.clieop_date_entry.get_text()+". Expecting YYYY-MM-DD).")
            return

        for txn in self.banking_transactions_model:
            if not txn[BankingTransactionsCols.INCLUDE]:
                continue
            desc = ' '.join([txn[BankingTransactionsCols.INVOICEID],txn[BankingTransactionsCols.DESCRIPTION]])
            amount = txn[BankingTransactionsCols.AMOUNT]
            acctholder = txn[BankingTransactionsCols.ACCOUNTHOLDER]
            acctnumber = txn[BankingTransactionsCols.ACCOUNTNUMBER]
            if not clieop03.AccountNumbers.isValid(acctnumber):
                showErrorMessage("Invalid accountnumber '"+str(acctnumber)+"' of '"+str(acctholder)+"' for '"+desc+"'")
                return
            onzuiver = not clieop03.AccountNumbers.canBeElfChecked(acctnumber)
            if onzuiver and not acctholder:
                showErrorMessage("Giro accountnumber without name for '"+desc+"'")
                return

            p = clieop03.Post()
            p.onzuiver = onzuiver
            p.bedrag = int(round(amount*100))
            p.omschrijving = desc
            if self.banking_mode == 'Payables':
                p.transactieSoort = clieop03.Post.ZAKELIJKE_BETALING
                p.rekeningnummerBegunstigde = acctnumber
                p.naamBegunstigde = acctholder
                p.rekeningnummerBetaler = self.app.accountnumber
            elif self.banking_mode == 'Receivables':
                p.transactieSoort = clieop03.Post.INCASSO_OPDRACHT
                p.rekeningnummerBetaler = acctnumber
                p.naamBetaler = acctholder
                p.rekeningnummerBegunstigde = self.app.accountnumber
            batch.posten.append(p)

        bestand.batches.append(batch)

        try:
            bestand.output(clieop03.ClieopWriter(io))
            self.app.set_status_text("Clieop file "+io_file+" succesfully generated.")
        except Exception as e:
            io.close()
            os.remove(io_file)
            showErrorMessage("Error generating "+io_file+".")
            print e
        else:
            io.close()
            self.banking_transactions_selector.set_active(False)
            for txn in self.banking_transactions_model:
                txn[BankingTransactionsCols.INCLUDE] = False


    def on_bank_accountholder_changed(self,entry):
        self.conf.set_string(GCSocietyApp.ACCOUNTHOLDER_KEY,entry.get_text())

    def on_bank_accountnumber_changed(self,entry):
        try:
            num = int(entry.get_text())
            self.conf.set_int(GCSocietyApp.ACCOUNTNUMBER_KEY,num)
        except:
            entry.set_text('')

    def on_clieopfile_select(self,button):
        e = self.banking_clieopfile_entry
        f = showSaveDialog(self.banking_clieopfile_entry,"Save Clieop03 File", e.get_text())
        f and e.set_text(f)
