#!/usr/bin/python
# -*- coding: utf-8 -*-

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
import sys
import math

from properties_object import PropertiesObject

class Bestand(PropertiesObject):

    def __init__(self):
        PropertiesObject.__init__(self,{
            'aanmaakDatum': date.today(),
            'duplicaat': False,
            'inzenderIdentificatie': '',
            'bestandVolgnummer': 1,
            'batches': [],
        })

    def check(self):
        assert self.aanmaakDatum != None
        assert len(self.batches) > 0
        tg = self.batches[0].transactieGroep
        i = 1
        for batch in self.batches:
            assert batch.transactieGroep == tg
            batch.batchVolgnummer = i
            batch.check()
            i = i+1

    def output(self,io):
        self.check()
        self.__Bestandvoorlooprecord(io)
        for batch in self.batches:
            batch.output(io)
        self.__Bestandsluitrecord(io)

    def __Bestandvoorlooprecord(self,io):
        io.N(4,1)
        io.X(1,'A')
        io.D(self.aanmaakDatum) # ddmmjj
        io.X(8,'CLIEOP03') # 'CLIEOP03'
        io.X(5,self.inzenderIdentificatie) # vrij
        io.X(4,self.aanmaakDatum.strftime('%d')+('%2s'%self.bestandVolgnummer)) # ddXX, dd = maanddag van de aanmaakdatum, XX = vanaf 1 oplopend volgnummer vanaf de maanddag waarop aanlevering heeft plaatsgevonden ???
        io.N(1, ( self.duplicaat and 2 ) or 1 ) # 1 = unicaat, 2 = duplicaat
        io.X(21,'')
        io.endRecord()

    def __Bestandsluitrecord(self,io):
        io.N(4,9999)
        io.X(1,'A')
        io.X(45,'')
        io.endRecord()

class Batch(PropertiesObject):

    ZAKELIJKE_BETALINGEN = '00'
    INCASSO_OPDRACHTEN = '10'
    
    NAAM_NIET_GEWENST = 1
    NAAM_GEWENST = 2

    def __init__(self):    
        self.__totaalBedrag = -1
        self.__totaalRekeningnummers = -1
        PropertiesObject.__init__(self,{
            'transactieGroep': Batch.ZAKELIJKE_BETALINGEN,
            'rekeningnummerOpdrachtgever': 0,
            'batchVolgnummer': 1,
            'batchIdentificatie': '',
            'vasteOmschrijving': '',
            'nawCode': Batch.NAAM_NIET_GEWENST,
            'gewensteVerwerkingsDatum': date.today(),
            'naamOpdrachtgever': '',
            'productie': False,
            'posten': [],
        })

    def check(self):
        AccountNumbers.assertValid(self.rekeningnummerOpdrachtgever)
        assert self.batchVolgnummer > 0
        assert len(partition(32, self.vasteOmschrijving)) < 5

        assert self.gewensteVerwerkingsDatum != None
        assert self.gewensteVerwerkingsDatum >= date.today()

        assert len(self.naamOpdrachtgever) > 0
        assert len(self.posten) > 0
        assert len(self.posten) < 100000
        self.__totaalBedrag = 0
        self.__totaalRekeningnummers = 0
        reks = set()
        for post in self.posten:
            post.check()
            if self.transactieGroep == Batch.ZAKELIJKE_BETALINGEN:
                assert post.transactieSoort == Post.ZAKELIJKE_BETALING or post.transactieSoort == Post.SALARIS_BETALING
            else:
                assert post.transactieSoort == Post.INCASSO_OPDRACHT
            self.__totaalRekeningnummers += post.rekeningnummerBegunstigde
            self.__totaalRekeningnummers += post.rekeningnummerBetaler
            self.__totaalBedrag += post.bedrag
            reks.add(post.rekeningnummerBetaler)
            reks.add(post.rekeningnummerBegunstigde)

    def output(self,io):
        self.check()
        self.__Batchvoorlooprecord(io)
        for omschrijving in partition(32, self.vasteOmschrijving):
            self.__VasteOmschrijvingRecord(io,omschrijving)
        self.__OpdrachtgeverRecord(io)
        for post in self.posten:
            post.output(io)
        self.__BatchSluitRecord(io)
    
    def __Batchvoorlooprecord(self,io):
        io.N(4,10) # 10
        io.X(1, ( len(self.batchIdentificatie) > 0 and 'C' ) or 'B' ) # 'B' = batchIdentificate rubriek bevat spaties , 'C' = batchIdentificate rubriek bevat een referentie van de inzender komt in boekingsinfo
        io.X(2,self.transactieGroep) # '00' = zakelijke betalingen, '10' = incasso opdrachten
        io.N(10,self.rekeningnummerOpdrachtgever)
        io.N(4,self.batchVolgnummer) # opvolgend, beginnend bij 1
        io.X(3,'EUR') # 'EUR'
        io.X(16,self.batchIdentificatie) # vrij, afhankelijk van variantCode
        io.X(10,'')
        io.endRecord()

    # 0-4
    def __VasteOmschrijvingRecord(self,io,omschrijving):
        io.N(4,20) # 20
        io.X(1,'A') # 'A'
        io.X(32,omschrijving) # Komt bij de info van alle posten, voor de individuele omschrijving. Deze omschrijving komt voor de omschrijving van een post en kan deze te lang maken, waardoor info wegvalt!!
        io.X(13,'')
        io.endRecord()
      
    # 1
    def __OpdrachtgeverRecord(self,io):
        io.N(4,30) # 30
        io.X(1,'B') # 'B'
        io.N(1,self.nawCode) # 1 = naam niet gewenst of n.v.t., 2 = naam gewenst (alleen bij zakelijke betaling, geeft aan of opdrachtgever namen wil ontvangen)
        io.D(self.gewensteVerwerkingsDatum) # ddmmjj / nullen is zo snel mogelijk, anders nu-5 < datum < nu+30
        io.X(35,self.naamOpdrachtgever) # optioneel
        pc = 'T'
        if self.productie:
            pc = 'P'
        io.X(1,pc) # 'P' = productie, 'T' = test
        io.X(2,'')
        io.endRecord()

    # 1
    def __BatchSluitRecord(self,io):
        io.N(4,9990) # 9990
        io.X(1,'A') # 'A'
        io.N(18,self.__totaalBedrag) # totaalbedrag (in centen?), maximum EUR 45.378.021.609,01
        rekCheck = '%010d' % self.__totaalRekeningnummers
        rekCheck = rekCheck[-10:]
        io.X(10,rekCheck) # som van de rubrieken rekeningnummer betaler en rekeningnummer opdrachtgever.
        pass              #Als te lang, alleen de rechter tien cijfers. Weiger batch als controle faalt.
        io.N(7,len(self.posten)) # max(100000)
        io.X(10,'')
        io.endRecord()

class Post(PropertiesObject):

    ZAKELIJKE_BETALING = 1
    SALARIS_BETALING = 2
    INCASSO_OPDRACHT = 3

    def __init__(self):
        PropertiesObject.__init__(self,{
            'transactieSoort': Post.ZAKELIJKE_BETALING,
            'onzuiver': False,
            'bedrag': 0,
            'rekeningnummerBetaler': 0,
            'naamBetaler': '',
            'rekeningnummerBegunstigde': 0,
            'naamBegunstigde': '',
            'betalingskenmerk': '',
            'omschrijving': '',
        })

    def check(self):
        AccountNumbers.assertValid(self.rekeningnummerBetaler)
        AccountNumbers.assertValid(self.rekeningnummerBegunstigde)
        assert self.bedrag % 1 == 0
        if self.transactieSoort == Post.ZAKELIJKE_BETALING or self.transactieSoort == Post.SALARIS_BETALING:
            assert not ( self.onzuiver and AccountNumbers.canBeElfChecked(self.rekeningnummerBegunstigde) )
            assert not self.onzuiver or len(self.naamBegunstigde) > 0
        else:
            assert not ( self.onzuiver and AccountNumbers.canBeElfChecked(self.rekeningnummerBetaler) )
            assert not self.onzuiver or len(self.naamBetaler) > 0
        pc = 0
        if len(self.betalingskenmerk) > 0:
            pc = pc + 1
        pc = pc + len(partition(32, self.omschrijving))
        assert pc > 0 and pc < 5

    def output(self,io):
        self.check()
        self.__TransactieRecord(io)
        if self.onzuiver and self.transactieSoort == Post.INCASSO_OPDRACHT:
            self.__NaamBetalerRecord(io)
        if len(self.betalingskenmerk) > 0:
            self.__BetalingskenmerkRecord(io)
        for omschrijving in partition(32, self.omschrijving):
            self.__OmschrijvingRecord(io,omschrijving)
        if self.onzuiver and ( self.transactieSoort == Post.ZAKELIJKE_BETALING or self.transactieSoort == Post.SALARIS_BETALING ):
            self.__NaamBegunstigdeRecord(io)
    
    def __getTransactieSoort(self):
        if ( self.transactieSoort == Post.ZAKELIJKE_BETALING and self.onzuiver ):
            return '0000'
        if ( self.transactieSoort == Post.SALARIS_BETALING and self.onzuiver ):
            return '0003'
        if ( self.transactieSoort == Post.ZAKELIJKE_BETALING and not self.onzuiver ):
            return '0005'
        if ( self.transactieSoort == Post.SALARIS_BETALING and not self.onzuiver ):
            return '0008'
        if ( self.transactieSoort == Post.INCASSO_OPDRACHT and not self.onzuiver ):
            return '1001'
        if ( self.transactieSoort == Post.INCASSO_OPDRACHT and self.onzuiver ):
            return '1002'

    # 1
    def __TransactieRecord(self,io):
        io.N(4,100) # 100
        io.X(1,'A') # 'A'
        io.X(4,self.__getTransactieSoort()) # '0000' onzuiver betaling, '0003' onzuiver salaris, '0005' gewoon of zuiver betaling, '0008' gewoon of zuiver salaris, '1001' gewoon of zuivere incasso, '1002' onzuiver incasso : onzuiver alleen als len(rekening) <= 7
        io.N(12,self.bedrag) # bedrag is centen, maximum is 453.780.216,08
        io.N(10,self.rekeningnummerBetaler) # moet bij zakelijke betalingen gelijk zijn aan rekeningnummer opdrachtgever
        io.N(10,self.rekeningnummerBegunstigde) # moet bij incasso gelijk zijn aan rekeningnummer opdrachtgever
        io.X(9,'')
        io.endRecord()
    
    # 0-1 (alleen bij onzuiver incasso opdracht)
    def __NaamBetalerRecord(self,io):
        io.N(4,110) # 110
        io.X(1,'B') # 'B'
        io.X(35,self.naamBetaler) # wordt tot positie 24 verwerkt
        io.X(10,'')
        io.endRecord()
    
    # 0-1
    def __BetalingskenmerkRecord(self,io):
        io.N(4,150) # 150
        io.X(1,'A') # 'A'
        io.X(16,self.betalingskenmerk) # vrij
        io.X(29,'')
        io.endRecord()

    # 0-4 als geen betalingskenmerk, 0-3 als betalingskenmerk
    def __OmschrijvingRecord(self,io,omschrijving):
        io.N(4,160) # 160
        io.X(1,'A') # 'A'
        io.X(32,omschrijving) # verplicht, niet naam opdrachtgever
        io.X(13,'')
        io.endRecord()
    
    # 0-1 (alleen bij onzuivere zakelijke betaling)
    def __NaamBegunstigdeRecord(self,io):
        io.N(4,170) # 170
        io.X(1,'B') # 'B'
        io.X(35,self.naamBegunstigde) # wordt tot positie 24 verwerkt
        io.X(10,'')
        io.endRecord()

class ClieopWriter:
    def __init__(self,io=sys.stdout):
        self.io = io
    
    __replacements = (
        (u'ÀÁÂÃÄÅÆ','A'),
        (u'Ç','C'),
        (u'ÈÉÊË','E'),
        (u'ÌÍÎÏ','I'),
        (u'Ñ','N'),
        (u'ÒÓÔÕÖØ','O'),
        (u'ÙÚÛÜ','U'),
        (u'ßŠ','S'),
        (u'š','s'),
        (u'àáâãäåæ','a'),
        (u'èéêë','e'),
        (u'ìíîï','i'),
        (u'ñ','n'),
        (u'òóôõöø','o'),
        (u'ùúûü','u'),
        (u'ýÿ','y'))
    def __cleanup(self,s):
        allowedChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZqwertyuioplkjhgfdsazxcvbnm1234567890 .()+&$*:;-/,%?@=\'"'
        r = ""
        for c in unicode(s):
            if c not in allowedChars:
                rc = '*'
                for ptrn, repl in self.__replacements:
                    if c in ptrn:
                        rc = repl
                c = rc
            r += c
        return r.encode('ascii')
    
    def X(self,num,value):
        fmt = '%-'+str(num)+'s'
        self.io.write(fmt % self.__cleanup(value))
    
    def N(self,num,value):
        assert value >= 0
        fmt = '%0'+str(num)+'d'
        self.io.write(fmt % value)
    
    def D(self,d):
        self.X(6,d.strftime('%d%m%y'))

    def endRecord(self):
        self.io.write('\r\n')

def partition(num,value):
    p = []
    np = int(math.ceil(len(value)/float(num)))
    for i in range(0,np):
        p.append(value[num*i:num*(i+1)])
    return p

class AccountNumbers:

    @staticmethod
    def assertValid(number):
        assert number != 0, "accountnumber %d is invalid" % number
        if AccountNumbers.canBeElfChecked(number):
            assert AccountNumbers.isElfCorrect(number), "accountnumber %d failed ELF test." % number

    @staticmethod
    def isValid(number):
        return number != 0 and ( not AccountNumbers.canBeElfChecked(number) or AccountNumbers.isElfCorrect(number) )
    
    @staticmethod
    def canBeElfChecked(number):
        return len(str(number)) > 7
    
    @staticmethod
    def isElfCorrect(number):
        elfstr = '%010d' % number 
        elf = 0
        for i in range(0,10):
            elf += (10-i) * int(elfstr[i])
        return (elf % 11) == 0

if __name__ == "__main__":
    io = ClieopWriter()
    #io = ClieopWriter(open("/home/hendrik/Desktop/test.clieop3",'w'))
    
    b = Bestand()
    
    b1 = Batch()
    b1.transactieGroep = Batch.INCASSO_OPDRACHTEN
    b1.naamOpdrachtgever = "SOSALSA"
    b1.rekeningnummerOpdrachtgever = 414853415
    b1.productie = False
    b1.gewensteVerwerkingsDatum = date.today()
    b1.vasteOmschrijving = "Contributie"
    
    for i in range(0,10):
        p = Post()
        p.transactieSoort = Post.INCASSO_OPDRACHT
        p.bedrag = 1295
        p.rekeningnummerBegunstigde = 414853415
        p.rekeningnummerBetaler = 383472075
        p.naamBetaler = "Hendrik"
        p.onzuiver = False
        p.omschrijving = "Some reason"
        b1.posten.append(p)
    
        p = Post()
        p.transactieSoort = Post.INCASSO_OPDRACHT
        p.bedrag = 1475
        p.rekeningnummerBegunstigde = 414853415
        p.rekeningnummerBetaler = 7361194
        p.naamBetaler = "Hendrik"
        p.onzuiver = True
        p.omschrijving = "Some other reason"
        b1.posten.append(p)
    
    b.batches.append(b1)
    b.check()
    b.output(io)
