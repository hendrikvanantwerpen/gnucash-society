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

from gnucash import Session, \
    ACCT_TYPE_ASSET, ACCT_TYPE_LIABILITY, \
    ACCT_TYPE_PAYABLE, ACCT_TYPE_RECEIVABLE, \
    ACCT_TYPE_EXPENSE

ACCOUNT_RECEIVABLE = 'Assets.Accounts Receivable'
ACCOUNT_PAYABLE = 'Liabilities.Accounts Payable'

ACCOUNT_BTW_COLLECTED_HIGH = 'Liabilities.BTW Collected.High'
ACCOUNT_BTW_REPORTED_HIGH = 'Liabilities.BTW Collected.High.Return'
ACCOUNT_BTW_COLLECTED_LOW = 'Liabilities.BTW Collected.Low'
ACCOUNT_BTW_REPORTED_LOW = 'Liabilities.BTW Collected.Low.Return'
ACCOUNT_BTW_COLLECTED_IMPORT = 'Liabilities.BTW Collected.Import'
ACCOUNT_BTW_REPORTED_IMPORT = 'Liabilities.BTW Collected.Import.Return'
ACCOUNT_BTW_PAID_NL = 'Assets.BTW Paid (NL)'
ACCOUNT_BTW_REPORTED_NL = 'Assets.BTW Paid (NL).Return'
ACCOUNT_BTW_PAID_EU = 'Assets.BTW Paid (EU)'
ACCOUNT_BTW_REPORTED_EU = 'Assets.BTW Paid (EU).Return'
ACCOUNT_TAX_EXPENSE = 'Expense.Taxes.BTW'

class Accounting:

    def __init__(self,filename):
        self.closed = False

        self.session = Session(filename)
        self.book = self.session.book
        commod_table = self.book.get_table()
        self.EUR = commod_table.lookup('CURRENCY', 'EUR')
        
        self.receivables = self._get_account(ACCOUNT_RECEIVABLE,ACCT_TYPE_RECEIVABLE);
        self.payables = self._get_account(ACCOUNT_PAYABLE,ACCT_TYPE_PAYABLE);
        
        self.btw_collected_high = self._get_account(ACCOUNT_BTW_COLLECTED_HIGH,ACCT_TYPE_LIABILITY);
        self.btw_reported_high = self._get_account(ACCOUNT_BTW_REPORTED_HIGH,ACCT_TYPE_LIABILITY);
        self.btw_collected_low = self._get_account(ACCOUNT_BTW_COLLECTED_LOW,ACCT_TYPE_LIABILITY);
        self.btw_reported_low = self._get_account(ACCOUNT_BTW_REPORTED_LOW,ACCT_TYPE_LIABILITY);
        self.btw_collected_import = self._get_account(ACCOUNT_BTW_COLLECTED_IMPORT,ACCT_TYPE_LIABILITY);
        self.btw_reported_import = self._get_account(ACCOUNT_BTW_REPORTED_IMPORT,ACCT_TYPE_LIABILITY);
        self.btw_paid_nl = self._get_account(ACCOUNT_BTW_PAID_NL,ACCT_TYPE_ASSET);
        self.btw_reported_nl = self._get_account(ACCOUNT_BTW_REPORTED_NL,ACCT_TYPE_ASSET);
        self.btw_paid_eu = self._get_account(ACCOUNT_BTW_PAID_EU,ACCT_TYPE_ASSET);
        self.btw_reported_eu = self._get_account(ACCOUNT_BTW_REPORTED_EU,ACCT_TYPE_ASSET);
        self.btw_reported_eu = self._get_account(ACCOUNT_BTW_REPORTED_EU,ACCT_TYPE_ASSET);
        self.tax_expense = self._get_account(ACCOUNT_TAX_EXPENSE,ACCT_TYPE_EXPENSE);

        self.taxtables = self.book.TaxTableGetTables()

    def _get_account(self,name,acct_type):
        root = self.book.get_root_account()
        acct = root.lookup_by_full_name(name)
        if acct.GetType() != acct_type:
            raise Exception('Account '+name+' does not exist with type '+str(acct_type))
        return acct

    def save(self):
        self.session.save()

    def close(self):
        if not self.closed:
            self.session.end()
            self.closed = True

    def __del__(self):
        self.close()

if __name__ == "__main__":
    raise Exception('Cannot be run directly')
