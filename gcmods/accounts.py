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
