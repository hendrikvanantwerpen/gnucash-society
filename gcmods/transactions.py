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

from datetime import datetime, timedelta

from gnucash import GncLot, ACCT_TYPE_PAYABLE, ACCT_TYPE_RECEIVABLE

from mods.enum import enum
from mods.structured_comment import StructuredComment
from mods.properties_object import PropertiesObject

from contacts import Contact

class Transaction(PropertiesObject):
    def __init__(self,initial=None):
        PropertiesObject.__init__(self,[ 'description', 'amount', 'invoiceid', 'owner', 'accountholder', 'accountnumber', 'allowincasso' ], initial)

class Unreconciled:

    Type = enum('RECEIVABLES','PAYABLES')

    def __init__(self,accounting,transaction_type):
        self.accounting = accounting
        self.transaction_type = transaction_type
        if transaction_type == Unreconciled.Type.RECEIVABLES:
            self.acct1 = accounting.receivables
            self.acct2 = accounting.payables
            self.comp = lambda x: x.to_double() > 0
            self.conv = lambda x: x.to_double()
        elif transaction_type == Unreconciled.Type.PAYABLES:
            self.acct1 = accounting.payables
            self.acct2 = accounting.receivables
            self.comp = lambda x: x.to_double() < 0
            self.conv = lambda x: -x.to_double()
        else:
            raise "Unknown transaction type %s" % transaction_type

    def get(self):
        items = []

        # Free splits
        splits = self.acct1.GetSplitList()
        splits = filter(lambda s: s.GetLot() == None and self.comp(s.GetAmount()), splits)
        self._fill_from_splits(items,splits)

        # unfinished lots
        lots = [ GncLot(instance=item) for item in self.acct1.GetLotList() ]
        lots = filter(lambda l: not l.is_closed() and self.comp(l.get_balance()), lots)
        self._fill_from_lots(items,lots)

        # overpaid or overreceived lots
        lots = [ GncLot(instance=item) for item in self.acct2.GetLotList() ]
        lots = filter(lambda l: not l.is_closed() and self.comp(l.get_balance()), lots)
        self._fill_from_lots(items,lots)

        return items

    def _fill_from_splits(self,items,splits):
        for split in splits:
            items.append(Transaction({
                'description': split.GetMemo() or self._get_txn_desc(split.GetParent()),
                'amount': self.conv(split.GetAmount()),
            }))
        return items

    def _fill_from_lots(self,items,lots):
        for lot in lots:
            invoice = lot.GetInvoiceFromLot()
            if invoice:
                sc = StructuredComment(invoice.GetNotes())
                owner = invoice.GetOwner()
                items.append(Transaction({
                    'description': self._get_txn_desc(invoice.GetPostedTxn()),
                    'amount': self.conv(lot.get_balance()),
                    'invoiceid': invoice.GetID(),
                    'owner': owner and Contact(owner),
                    'accountholder': sc.get_string('AccountHolder'),
                    'accountnumber': sc.get_int('AccountNumber'),
                    'allowincasso': sc.get_bool('AllowIncasso'),
                }))
            else:
                items.append(Transaction({
                    'amount': self.conv(lot.get_balance()),
                    'invoiceid': lot.get_title(),
                }))
        return items

    def _get_txn_desc(self,txn):
        return txn.GetSplit(0).GetMemo() or txn.GetDescription()
