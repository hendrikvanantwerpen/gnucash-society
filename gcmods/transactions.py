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
