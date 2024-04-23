#!/usr/bin/python3
# -*- coding: utf-8 -*-

from difflib import SequenceMatcher
import logging
import re

class Provenance:
    def __init__(self, chain = None, position = None):
        self.chain = ""
        if chain != None:
            self.chain = chain
        self.errors = []
        self.name = ""
        self.descriptors = []
        self.date = ""
        self.position = ""
        if position != None:
            self.position = int(position)
        pieces = map(str.strip, self.chain.split("/"))
        for piece in pieces:
            if "Provenienz:" in piece:
                self.name = piece.replace("Provenienz:", "").strip()
            elif "Datum" in piece:
                self.date = piece.replace("Datum", "").strip()
                # Kaufdatum, Lesedatum und keine Angabe berücksichtigen
            else:
                self.descriptors.append(piece)
        self.valid = self.validate()
    def validate(self):
        if "!" in self.name:
            self.errors.append(f"Fehlerhafter Name: {self.name}")
        if "Provenienz: " not in self.chain:
            self.errors.append("Schlüsselwort Provenienz fehlt oder unvollständig")
            return(False)
        if self.position not in range(0, 10):
            self.errors.append(f"Provenienzkette außerhalb 68XX (Position: {int(self.position)})")
        test_date = re.search("[12][0-9]{3}(-[01][0-9])?(-[0123][0-9])?", self.date)
        if test_date == None and self.date != "":
            self.errors.append(f"Fehlerhaftes Datum: {self.date}")
            return(False)
        # Prüfen, ob die Deskriptoren im Thesaurus stehen. DEskriptor Ort (unzulässig) rausfiltern
        return(True)
    def __str__(self):
        ret = f"Provenienz: {self.name} / {' / '.join(self.descriptors)}"
        if self.date != "":
            ret = ret + " / Datum " + self.date
        #if self.position != "":
        #    ret = ret + ", Position: " + str(self.position)
        return(ret)

class ProvenanceBibLevel(Provenance):
    def __init__(self):
        super().__init__()
        self.gnd = None
        self.ppn = None
        self.isil = ""
        self.epn = ""
        self.sm = ""
        self.comment = ""
    def __str__(self):
        ret = f"Provenienz: {self.name}"
        if self.gnd != None:
            ret = ret + " " + self.gnd
        if self.descriptors != []:
            ret = ret + " / ".join(self.descriptors)
        if self.date != "":
            ret = ret + " / Datum " + self.date
        return(ret)
        
class NormLinkLocal:
    def __init__(self, name, ppn, position):
        self.pos_raw = position.strip()
        try:
            self.position = int(self.pos_raw) - 80
        except:
            pass
        self.name = name
        self.ppn = ppn
        self.errors = []
        self.valid = self.validate()           
    def validate(self):
        ret = True
        try:
            test1 = re.search("[89][0-9]|00", self.pos_raw) #00: Sonderfall Lessing in 6800
        except:
            return(False)
        try:
            test2 = re.search("[0-9]{8,12}", self.ppn)
        except:
            return(False)
        if test1 == None:
            self.errors.append(f"Ungültige Positionsangabe: \"{self.pos_raw}\"")
            ret = False
        if test2 == None:
            self.errors.append(f"Ungültige PPN: \"{self.ppn}\"")
            ret = False
        if self.name == "" or "!" in self.name:
            self.errors.append(f"Ungültiger Name: \"{self.name}\"")
            ret = False
        return(ret)
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
        for prov in self.provv:
            if prov.errors != []:
                self.errors.append(f"Fehler in Kette(n)~" + ";".join(prov.errors))
        for link in self.links:
            if link.errors != []:
                self.errors.append(f"Fehler in Verknüpfung(en)~" + ";".join(link.errors))
        prov_names = set([prov.name for prov in self.provv])
        link_names = set([link.name for link in self.links])
        single_pn = [name for name in prov_names if name not in link_names]
        ratios_pn = {}
        for name in single_pn:
            if name == "NN":
                continue
            for name_cmp in link_names:
                ratios_pn[name_cmp] = similar(name, name_cmp)
            if ratios_pn != {}:
                most_similar_pn = max(ratios_pn, key=lambda x: ratios_pn[x])
                self.errors.append(f"Abweichende Verknüpfung~Namen: \"{name}\"|\"{most_similar_pn}\"")
            else:
                self.errors.append(f"Keine Verknüpfung~Name: \"{name}\"")
        
    def print_errors(self):
        if self.errors == []:
            return(None)
        return(f"EPN {self.epn}: {' - '.join(self.errors)}")
                
def similar(a, b):
    a = normalize_name(a)
    b = normalize_name(b)
    return(SequenceMatcher(None, a, b).ratio())
    
def normalize_name(name):
    name = name.lower()
    repl = { "ä" : "ae", "ö" : "oe", "ü" : "ue", "ß" : "ss", " von" : "", "th" : "t" }
    for key in repl:
        name = name.replace(key, repl[key])
    return(name)