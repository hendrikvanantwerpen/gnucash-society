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

from datetime import date
import csv

from numeric import *

from gnucash import Split, GncNumeric

class AccountsFiltered:
    def __init__(self,account,accttype):
        self.account = account
        self.accttype = accttype

    def get_accounts(self):
        accounts = self.account.get_descendants_sorted()
        accounts = filter(lambda a: a.GetType() == self.accttype, accounts)
        return accounts

class AccountReport:

    def __init__(self, account, startdate, enddate, title=None):
        self.account = account
        self.title = title or self.account.get_full_name()
        self.startdate = startdate
        self.enddate = enddate
        self._get_splits()
        self._make_report()

    def _get_splits(self):
        self.splits = self.account.GetSplitList()
        def f(x):
            txn = x.GetParent()
            txn_date = date.fromtimestamp(txn.GetDate())
            return txn_date >= self.startdate and txn_date <= self.enddate
        self.splits = filter(f, self.splits)

    def _make_report(self):
        self.total = GncNumeric()
        self.entries = []
        for split in self.splits:
            txn = split.GetParent()
            desc = txn.GetDescription()
            memo = split.GetMemo()
            txn_date = date.fromtimestamp(txn.GetDate())
            amount = split.GetValue()
            self.total = self.total.add_fixed(amount)
            self.entries.append({
                'date': txn_date,
                'owner': desc,
                'desc': memo,
                'amount': amount,
            })
        (self.report_total,self.report_rest) = gncn_round_with_rest(self.total)

    def write(self,io):
        w = csv.writer(io)
        w.writerow([])
        w.writerow(['Name',self.title])
        w.writerow(['Total',self.total])
        w.writerow(['Report Total',str(self.report_total)])
        w.writerow(['Report Rest',str(self.report_rest)])
        w.writerow(['Transactions','Date','Owner','Description','Amount'])
        for entry in self.entries:
            w.writerow(['',entry['date'],entry['owner'],entry['desc'],str(entry['amount'])])
        w.writerow([])
