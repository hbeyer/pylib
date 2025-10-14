#!/usr/bin/python3
# -*- coding: utf-8 -*-

from difflib import SequenceMatcher
from lib import tpro
import logging
import re

class Provenance:
    def __init__(self, chain = None, position = None):
        self.chain = ""
        if chain != None:
            self.chain = chain
        self.errors = []
        self.name = ""
        self.testInst = ""
        self.descriptors = []
        self.date = ""
        self.position = ""
        if position != None:
            self.position = int(position)
        # Das Folgende behebt ein Spezialproblem (Unterinstitutionen mit Schrägstrich) für den Datenbestand der HAB
        for inst in inst_list:
            if inst in self.chain:
                self.name = inst
                self.chain = self.chain.replace(inst, "").strip()
                #logging.info(f"Institution erkannt: {inst}")
                break
        # Ende Problembehebung
        pieces = map(str.strip, self.chain.split("/"))
        timedescrr = ["Datum", "Kaufdatum", "Lesedatum"]
        for piece in pieces:
            time = False
            if "Provenienz:" in piece:
                self.name = piece.replace("Provenienz:", "").strip()
                continue
            for timedescr in timedescrr:
                if timedescr in piece:
                    self.date = piece.replace(timedescr, "").strip()
                    self.descriptors.append(timedescr)
                    time = True
                    break
            if time == False:
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
        invalid_descr = []
        for count, descr in enumerate(self.descriptors):
            if tpro.validate(descr) == False:
                invalid_descr.append(descr)
                if count == 0:
                    self.testInst = self.name + " / " + descr
        if len(invalid_descr) == 1:
            self.errors.append(f"Ungültiger Deskriptor: {invalid_descr[0]}")
            return(False)
        elif len(invalid_descr) > 1:
            self.errors.append(f"Ungültige Deskriptoren: {';'.join(invalid_descr)}")
            return(False)
        return(True)
    def __str__(self):
        ret = f"Provenienz: {self.name} / {' / '.join(self.descriptors)}"
        if self.date != "":
            ret = ret + " / Datum " + self.date
        ret = f"{ret}, Position: {str(self.position)}"
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
        prov_positions = { prov.name : [] for prov in self.provv }
        for prov in self.provv:
            prov_positions[prov.name].append(prov.position)
        for lnk in self.links:
            if lnk.name not in prov_names:
                if lnk.name != "Lessing, Gotthold Ephraim":
                    most_similar_pn = get_most_sim(lnk.name, prov_names)
                    self.errors.append(f"Kein korrespondierender Name in Kette~{lnk.name}|{most_similar_pn}")
            else:
                if lnk.position not in prov_positions[lnk.name]:
                    self.errors.append(f"Abweichende Positionen~{lnk.name} {str(lnk.position)}|{','.join(map(str, prov_positions[lnk.name]))}")
    def print_errors(self):
        if self.errors == []:
            return(None)
        return(f"EPN {self.epn}: {' - '.join(self.errors)}")
                
def similar(a, b):
    a = normalize_name(a)
    b = normalize_name(b)
    return(SequenceMatcher(None, a, b).ratio())

def get_most_sim(needle, hay):
    ratios_pn = {}
    for name_cmp in hay:
        ratios_pn[name_cmp] = similar(needle, name_cmp)
    if ratios_pn != {}:
        return(max(ratios_pn, key=lambda x: ratios_pn[x]))
    return("")
    
def normalize_name(name):
    name = name.lower()
    repl = { "ä" : "ae", "ö" : "oe", "ü" : "ue", "ß" : "ss", " von" : "", "th" : "t" }
    for key in repl:
        name = name.replace(key, repl[key])
    return(name)
    
# Institutionen mit Schrägstrich, die in Provenienzketten der HAB vorhanden sind
inst_list = [
    "Technische Universität Dresden / Bibliothek", 
    "Hessen / Offenbach Archival Depot", 
    "Ordo Fratrum Minorum Capuccinorum / Zentralbibliothek", 
    "Braunschweig <Staat> / Obergericht", 
    "Franckesche Stiftungen zu Halle / Buchhandlung", 
    "Universitatea din București / Biblioteca", 
    "Paris <17. Arrondissement> / Bibliothèque municipale", 
    "Sankt Maria in der Au / Kloster", 
    "Stadtarchiv <Meißen> / Bücherei", 
    "Minoriták <Szeged> / Könyvtár", 
    "Uniwersytet Imienia Adama Mickiewicza <Poznań> / Biblioteka", 
    "St. Joseph's College <Mill Hill> / Library", 
    "Rostocksche Academie / Bibliothek", 
    "Ericsbergs slott / Bibliotek", 
    "Szegedi Tudomanyegyetem / Bibliothek", 
    "Mecklenburg-Schwerin / Landgericht Rostock", 
    "Staat Braunschweig / Bau-Direction", 
    "Societatis Jesu / Domus <Wien>", 
    "Karmelitenkloster <Frankfurt / Main>", 
    "Magyar Nemzeti Múzeum <Budapest> / Bibliothek", 
    "M. Kir. Erzsebet Tud. Egyetem <Pecs> / Bibliothek", 
    "Ordo Fratrum Minorum / Schlesische Franziskanerprovinz", 
    "Braunschweig <Staat> / Kreisgericht <Braunschweig>", 
    "Societas Jesu / Domus <Wien>", 
    "Baltic University / Bibliothek", 
    "Steyler Missionare / Bibliothek", 
    "Gymnasium <Greifswald> / Lehrerbibliothek", 
    "Ackermann, J. C. D. / Leihbibliothek", 
    "Regierungsbezirk Posen / Bibliothek", 
    "Karolinska Institutet <Stockholm> / Hagströmer Biblioteket", 
    "Franckesche Stiftungen zu Halle / Waisenhaus", 
    "Braunschweig <Staat> / Oberstaatsanwaltschaft", 
    "Ludwig-Maximilians-Universität München / Universitätsbibliothek", 
    "École Libre Saint-Joseph <Lille> / Bibliothèque", 
    "Fürstenschule St. Afra <Meißen> / Bibliothek", 
    "Gesellschaft für Geschichte in Altenburg / Bibliothek", 
    "Universität <Göttingen> / Seminar für Deutsche Philologie", 
    "Communauté Israélite <Strasbourg> / Bibliothèque", 
    "Braunschweig <Staat> / Amtsgericht <Blankenburg>", 
    "University <Keele> / Library", 
    "Ordo Fratrum Minorum Conventualium <Troppau> / Bibliothek", 
    "Ostdeutsches Heimatmuseum Nienburg <Weser> / Bibliothek Klaus Prassler", 
    "Kapuzinerkloster <Freiburg, Breisgau> / Missionsbibliothek", 
    "Société Géologique de France / Bibliothèque", 
    "Biblioteka Publiczna <Warschau> / Czytelnia naukowa", 
    "Ordo Fratrum Minorum / Sächsische Franziskanerprovinz vom Heiligen Kreuze", 
    "Technische Universität Dresden / Fakultät für Berufspädagogik und Kulturwissenschaften", 
    "Societas Jesu / English Province", 
    "Österreichische Nationalbibliothek / Fideikommißbibliothek", 
    "Magyar Tudományos Akadémia <Budapest> / Könyvtár", 
    "Deutsches Reich / Reichsgericht", 
    "Universität <Helmstedt> / Medizinische Fakultät", 
    "Technische Hochschule <Danzig> / Staatswissenschaftliches Seminar", 
    "New College London / General Library", 
    "Preußen / Oberbergamt <Halle, Saale>", 
    "Uniwersytet Wrocławski / Biblioteka", 
    "Magyar Nemzeti Múzeum <Budapest> / Könyvtár", 
    "Uniwersytet Mikołaja Kopernika w Toruniu / Biblioteka Uniwersytecka", 
    "Politechnika Gdańska / Biblioteka Główna", 
    "Ordo Fratrum Minorum Capuccinorum / Bayerische Provinz", 
    "Gesellschaft für Anthropologie und Urgeschichte der Oberlausitz / Zweigverein Görlitz", 
    "Universität Helmstedt / Medizinische Fakultät", 
    "Universitatea din București / Facultatea de Teologie Ortodoxă", 
    "Paris <12. Arrondissement> / Bibliothèque municipale", 
    "Vrije Universiteit <Amsterdam> / Bibliotheek", 
    "Redemptoristen / Niederdeutsche Provinz", 
    "Katholische Kirche <Erzdiözese Paris> / Archiv", 
    "Paris <19. Arrondissement> / Bibliothèque municipale", 
    "Academy Hoxton / Library", 
    "Propstei <Münsterdorf> / Kirche Itzehoe", 
    "Rijksuniversiteit <Leiden> / Bibliotheek", 
    "Staatliche Museen zu Berlin (Berlin, Ost) / Zentralbibliothek", 
    "Universität <Göttingen> / Theaterwissenschaftliches Seminar", 
    "Braunschweig <Staat> / Handelsgericht", 
    "Heythrop College <London> / Library", 
    "Reemtsma-Cigarettenfabriken <Hamburg> / Tabakmuseum", 
    "Braunschweig <Staat> / Kreisgericht <Blankenburg>", 
    "Universität <Rostock> / Alttestamentliches Seminar", 
    "Paris <2. Arrondissement> / Bibliothèque municipale", 
    "Congregatio Sanctissimi Redemptoris / Österreichische Provinz", 
    "Industrie- und Handelskammer zu Leipzig / Bücherei", 
    "Congregatio Sanctissimi Redemptoris / Wiener Provinz <Mautern, Steiermark>", 
    "Komitat Somogy / Könyvtár", 
    "Braunschweig-Wolfenbüttel / Fürstliche Kanzlei", 
    "Königliche Technische Hochschule Danzig / Bücherei", 
    "Königliche Museen  zu Berlin / Bibliothek", 
    "Braunschweig <Staat> / Amtsgericht <Thedinghausen>", 
    "Braunschweig / Rat", 
    "Landesstrafanstalt <Wolfenbüttel> / Buchbinderei", 
    "Országos Könyvtári Központ <Budapešt> / Raktar <Szeged >", 
    "Kapuziner / Province Belge", 
    "Franziskanerkonvent / <Wien>", 
    "Braunschweig <Staat> / Kreisgericht <Holzminden>", 
    "Paris <6. Arrondissement> / Bibliothèque municipale"
]    