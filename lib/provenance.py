#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re

class Provenance:
    def __init__(self, chain, position = None):
        self.chain = chain
        self.name = ""
        self.descriptors = []
        self.date = ""
        self.position = ""
        if position != None:
            self.position = int(position)
        pieces = map(str.strip, chain.split("/"))
        for piece in pieces:
            if "Provenienz:" in piece:
                self.name = piece.replace("Provenienz:", "").strip()
            elif "Datum" in piece:
                self.date = piece.replace("Datum", "").strip()
            else:
                self.descriptors.append(piece)
        self.valid = self.validate()
    def validate(self):
        if "Provenienz: " not in self.chain:
            return(False)
        test = re.search("[12][0-9]{3}(-[01][0-9])?(-[0123][0-9])?", self.date)
        if test == None and self.date != "":
            return(False)
        return(True)
    def __str__(self):
        ret = f"Provenienz: {self.name} / {' / '.join(self.descriptors)}"
        if self.date != "":
            ret = ret + " / Datum " + self.date
        if self.position != "":
            ret = ret + ", Position: " + str(self.position)
        return(ret)
        
class NormLinkLocal:
    def __init__(self, name, ppn, position):
        self.pos_raw = position.strip()
        self.name = name
        self.ppn = ppn
        self.valid = False
        test1 = re.search("[89][0-9]|00", self.pos_raw) #00: Sonderfall Lessing in 6800
        test2 = re.search("[0-9]{8,12}", self.ppn)
        if test1 and test2:
            self.position = int(self.pos_raw) - 80
            self.valid = True

    def __str__(self):
        if self.valid == True:
            return(f"Verknüpfung: {self.name}, PPN {self.ppn}, Position: {int(self.position)}")
        return(f"Verknüpfung: {self.name}, PPN {self.ppn}, Position: {self.pos_raw}, FEHLER")
        
class Dataset:
    def __init__(self, epn, provv = None, links = None):
        self.epn = epn
        self.errors = []
        self.provv = []
        if provv != None:
            for prov in provv:
                if prov.__class__.__name__ == "Provenance":
                    self.provv.append(prov)
        self.links = []
        if links != None:
            for link in links:
                if link.__class__.__name__ == "NormLinkLocal":
                    self.links.append(link)
        self.check()
    def check(self):
        #names = [link.name for link in self.links]
        prov_names = [prov.name for prov in self.provv]
        for prov in self.provv:
            """"if prov.name not in names:
                self.errors.append(f"{prov.name} nicht in Normdatenverknüpfung")"""
            if prov.valid != True:
                self.errors.append(f"FEHLER: {str(prov)}")
        for link in self.links:
            if link.name not in prov_names:
                self.errors.append(f"{link.name} nicht in Provenienzkette")
            if link.valid != True:
                self.errors.append(f"FEHLER: {str(link)}")
    def print_errors(self):
        if self.errors == []:
            return(None)
        return(f"EPN {self.epn}: {' - '.join(self.errors)}")