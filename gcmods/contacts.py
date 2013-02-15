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

import csv

from gnucash import Query
from gnucash.gnucash_business import Customer, Vendor
from gnucash._gnucash_core_c import GNC_ID_CUSTOMER, GNC_ID_VENDOR

from mods.structured_comment import StructuredComment
from mods.properties_object import PropertiesObject

class Contact(PropertiesObject):
    def __init__(self,owner=None):
        PropertiesObject.__init__(self,[ 'id', 'name', 'accountholder', 'accountnumber', 'allowincasso', 'owner' ])
        if owner:
            self.owner = owner
            self.id = owner.GetID()
            self.name = owner.GetName()
            sc = StructuredComment(owner.GetNotes())
            self.accountholder = sc.get_string('AccountHolder')
            self.accountnumber = sc.get_int('AccountNumber')
            self.allowincasso = sc.get_bool('AllowIncasso')

class Contacts:

    def __init__(self,accounting):
        self.accounting = accounting

    def get_customers(self):
        q = Query()
        q.set_book(self.accounting.book)
        q.search_for(GNC_ID_CUSTOMER)
        items = [ Contact(Customer(instance=item)) for item in q.run() ]
        return items

    def get_vendors(self):
        q = Query()
        q.set_book(self.accounting.book)
        q.search_for(GNC_ID_VENDOR)
        items = [ Contact(Vendor(instance=item)) for item in q.run() ]
        return items

class ContactsSync:

    def __init__(self,accounting,filename):
        self.accounting = accounting
        self.mapping = Contact()
        self.csv = csv.DictReader(open(filename,'rb'))

    def get_headers(self):
        return self.csv.fieldnames

    def set_mapping(self,field,csvfield):
        if csvfield and csvfield not in self.csv.fieldnames:
            raise "%s is not a valid header." % csvfield
        self.mapping[field] = csvfield

    def sync(self):
        if not self.mapping['id']:
            raise "Provide at least a mapping for 'id'."

        for row in self.csv:
            (c,v) = self._get_contact(row)
            self._update_contact(c,row)
            self._update_contact(v,row)

        self.accounting.save()

    def _get_contact(self,row):
        id  = row[self.mapping['id']]
        book = self.accounting.book
        EUR = self.accounting.EUR
        customer = book.CustomerLookupByID(id)
        if not customer:
            customer = Customer(book,id,EUR,"Customer %s" % id)
        vendor = book.VendorLookupByID(id)
        if not vendor:
            vendor = Vendor(book,id,EUR,"Vendor %s" % id)
        return (customer,vendor)

    def _update_contact(self,c,row):
        sc = StructuredComment(c.GetNotes())

        fld = self.mapping['name']
        if fld:
            c.SetName(row[fld])
            a = c.GetAddr()
            a.SetName(row[fld])
            a.SetAddr1('-')

        fld = self.mapping['accountholder']
        if fld:
            key = 'AccountHolder'
            if row[fld]:
                sc.set_entry(key,row[fld])
            else:
                sc.remove_entry(key)

        fld = self.mapping['accountnumber']
        if fld:
            key = 'AccountNumber'
            try:
                sc.set_entry(key,int(row[fld]))
            except:
                sc.remove_entry(key)

        fld = self.mapping['allowincasso']
        if fld:
            key = 'AllowIncasso'
            val = row[fld].lower()
            if val:
                if val == 'true' or val == 'yes' or val == '1' or val == 'y':
                    sc.set_entry(key,True)
                else:
                    sc.set_entry(key,False)
            else:
                sc.remove_entry(key)

        c.SetNotes(sc.get_comment())

