#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import urllib.request as ul
import xml.etree.ElementTree as et
import re
import logging
from lib import isil
#from lib import xmlserializer as xs

class Record:
    def __init__(self, node):
        self.node = node
        self.data = {}
        self.persons = []
        self.copies = []
        self.places = []
        self.publishers = []
        self.vdn = ""
        self.get_data()
        try:
            self.ppn = self.data["003@"]["01"]["0"].pop(0)
        except:
            self.ppn = ""
        try:
            self.bbg = self.data["002@"]["01"]["0"].pop(0)
        except:
            self.bbg = ""
        bud = None
        try:
            bud = self.data["001A"]["01"]["0"].pop(0)
        except:
            pass
        else:
            self.isilRec = bud.split(":").pop(0)
            try:
                self.dateRec = bud.split(":").pop(1)
            except:
                pass
        try:
            self.catRule = self.data["010E"]["01"]["e"].pop(0)
        except:
            self.catRule = "rak"
        try:
            self.title = self.data["021A"]["01"]["a"].pop(0)
        except:
            try:
                self.title = self.data["047C"]["01"]["a"].pop(0)
            except:
                try:
                    self.title = self.data["036C"]["01"]["a"].pop()
                except:
                    self.title = ""
        try:
            self.title = self.title + ". " + self.data["021A"]["01"]["d"].pop(0)
        except:
            pass
        try:
            self.resp = self.data["021A"]["01"]["h"].pop(0)
        except:
            self.resp = ""
        try:
            self.lang = self.data["010@"]["01"]["a"]
        except:
            self.lang = []
        try:
            self.langOrig = self.data["010@"]["01"]["c"]
        except:
            self.langOrig = []
        self.gatt = []
        try:
            gatDict = self.data["044S"]
        except:
            pass
        else:
            for occ in gatDict:
                try:
                    self.gatt.extend(gatDict[occ]["a"])
                except:
                    pass
        self.gatt = map(lambda term: re.sub("\!.+\!", "", str(term)), self.gatt)
        self.subjects = []
        try:
            subDict = self.data["044K"]
        except:
            pass
        else:
            for occ in subDict:
                try:
                    self.subjects.append(subDict[occ]["a"].pop(0))
                except:
                    pass
        try:
            self.pages = self.data["034D"]["01"]["a"].pop(0)
        except:
            self.pages = ""
        self.normPages = 0
        if self.pages != "":
            self.normPages = get_norm_p(self.pages)
        try:
            self.format = self.data["034I"]["01"]["a"].pop(0)
        except:
            self.format = ""
        try:
            self.vd16m = self.data["006L"]["01"]["0"]
        except:
            self.vd16m = []
        try:
            self.date = self.data["011@"]["01"]["a"].pop(0)
        except:
            self.date = ""
        self.digi = []
        try:
            digiDict = self.data["017D"]
        except:
            pass
        else:
            for key in digiDict:
                try:
                    self.digi.extend(digiDict[key]["u"])
                except:
                    pass
        if self.bbg[0] == "O":
            try:
                self.digi = self.data["209R"]["01"]["u"].pop(0)
            except:
                pass
        self.load_persons()
        self.load_copies()
        self.load_places()
        self.load_publishers()
        self.get_vd()        
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", Jahr: " + self.date
        return(ret)
    def get_data(self):
        fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield")
        occDict = {}
        for fn in fields:
            tag = fn.get("tag")
            occ = fn.get("occurrence")
            if occ == None:
                try:
                    occDict[tag] += 1
                except:
                    occDict[tag] = 1
                occ = str(occDict[tag]).zfill(2)
            children = fn.findall("*")
            for ch in children:
                code = ch.get("code").lower()
                try:
                    self.data[tag][occ][code].append(ch.text)
                except:
                    try:
                        self.data[tag][occ][code] = [ch.text]
                    except:
                        try:
                            self.data[tag][occ] = { code: [ch.text] }
                        except:
                            try:
                                self.data[tag] = { occ: { code: [ch.text] } }
                            except:
                                pass
    def load_persons(self):
        try:
            creatorList = self.data["028A"]
        except:
            pass
        else:
            for occ in creatorList:
                per = Person()
                per.role = "creator"
                per.import_structdata(creatorList[occ])
                self.persons.append(per)
        try:
            creatorList2 = self.data["028B"]
        except:
            pass
        else:
            for occ in creatorList2:
                per = Person()
                per.role = "creator"
                per.import_structdata(creatorList2[occ])
                self.persons.append(per)
        try:
            contributorList = self.data["028C"]
        except:
            pass
        else:
            for occ in contributorList:
                per = Person()
                per.role = "contributor"
                per.import_structdata(contributorList[occ])
                self.persons.append(per)            
    def load_copies(self):
        try:
            sigRow = self.data["209A"]
        except:
            pass
        else:
            for occ in sigRow:
                try:
                    sm = sigRow[occ]["a"].pop(0)
                except:
                    sm = None
                else:
                    cp = Copy(sm)
                    try:
                        isil = self.data["202D"][occ]["a"].pop(0)
                    except:
                        pass
                    else:
                        cp.isil = isil
                    try:
                        cp.provenances = self.data["244Z"][occ]["a"]
                    except:
                        pass
                    self.copies.append(cp)
    def load_places(self):
        try:
            placeList = self.data["033D"]
        except:
            return(None)
        for occ in placeList:
            try:
                placeName = placeList[occ]["p"].pop(0)
            except:
                continue
            try:
                placeRel = placeList[occ]["4"].pop(0)
            except:
                placeRel = ""
            placeName = re.sub("\!.+\!", "", placeName)
            self.places.append(Place(placeName, placeRel))
    def load_publishers(self):
        try:
            pubRow = self.data["033J"]
        except:
            return(None)
        for occ in pubRow:
            pub = Person()
            pub.role = "publisher"
            pub.import_structdata(pubRow[occ])
            self.publishers.append(pub)
    def get_vd(self):
        try:
            self.vdn = self.data["006V"]["01"]["0"].pop(0)
        except:
            try:
                self.vdn = self.data["006W"]["01"]["0"].pop(0)
            except:
                try:
                    self.vdn = self.data["006M"]["01"]["0"].pop(0)
                except:
                    pass
    def to_dict(self):
        res = {
            "ppn" : self.ppn,
            "vdn" : self.vdn,
            "recType" : self.bbg,
            "catRule" : self.catRule,
            "date" : self.date,
            "lang" : ";".join(self.lang),
            "title" : self.title.replace("@", ""),
            "resp" : self.resp,
            "format" : self.format,
            "pages" : self.pages,
            "normPages" : str(self.normPages),
            }
        if self.langOrig != []:
            res["langOrig"] = ";".join(self.langOrig)
        if self.digi != []:
            res["digi"] = ";".join(self.digi)
        if self.gatt != []:
            res["gat"] = ";".join(self.gatt)
        if self.subjects != []:
            res["subjects"] = ";".join(self.subjects)
        if self.persons != []:
            res["persons"] = [pers.to_dict() for pers in self.persons]
        if self.publishers != []:
            res["publishers"] = [pers.to_dict() for pers in self.publishers]
        if self.places != []:
            res["places"] = [pl.to_dict() for pl in self.places]
        if self.copies != []:
            res["copies"] = [cp.to_dict() for cp in self.copies]
        return(res)
    def to_libreto(self, prov = None):
        itn = et.Element("item")
        et.SubElement(itn, "id").text = "lid" + self.ppn
        et.SubElement(itn, "titleCat").text = self.title
        if self.persons != []:
            persl = et.Element("persons")
            for pers in self.persons:
                persn = et.Element("person")
                et.SubElement(persn, "persName").text = pers.persName
                et.SubElement(persn, "gnd").text = pers.gnd
                et.SubElement(persn, "role").text = pers.role
                persl.append(persn)
            itn.append(persl) 
        if self.places != []:
            placel = et.Element("places")
            for pl in self.places:
                placen = et.Element("place")
                et.SubElement(placen, "placeName").text = pl.placeName
                if pl.gnd != None:
                    et.SubElement(placen, "gnd").text = pl.gnd
                placel.append(placen)
            itn.append(placel)
        if self.publishers != []:
            publ = et.Element("publishers")
            for pub in self.publishers:
                et.SubElement(publ, "publisher").text = pub.persName
            itn.append(publ)
        if self.date:
            et.SubElement(itn, "year").text = self.date
        if self.format:
            et.SubElement(itn, "format").text = self.format
        if self.lang != []:
            langl = et.Element("languages")
            for code in self.lang:
                et.SubElement(langl, "language").text = code
            itn.append(langl)
        letter = self.bbg[0]
        mediaType = assign_mediatype(letter)
        et.SubElement(itn, "mediaType").text = mediaType
        genrel = et.Element("genres")
        subjl = et.Element("subjects")
        numSubj = 0
        numGenres = 0
        for gat in self.gatt:
            if recognize_genre(gat) == "genre":
                et.SubElement(genrel, "genre").text = gat
                numGenres += 1
            else:
                et.SubElement(subjl, "subject").text = gat
                numSubj += 1
        if numGenres > 0:
            itn.append(genrel)
        if numSubj > 0:
            itn.append(subjl)
        mann = et.Element("manifestation")
        sysman = "K10plus"
        idman = self.ppn
        if self.vdn != "":
            if self.vdn[0:4] == "VD16":
                sysman = "VD16"
                idman = self.vdn
            elif self.vdn[0:4] == "VD17":
                sysman = "VD17"
                idman = self.vdn
            elif self.vdn[0:4] == "VD18":
                sysman = "VD18"
                idman = self.vdn                
        et.SubElement(mann, "systemManifestation").text = sysman
        et.SubElement(mann, "idManifestation").text = idman
        itn.append(mann)
        chab = et.Element("copiesHAB")
        numhab = 0
        for cop in self.copies:
            if "HAB" in cop.bib or "Herzog August" in cop.bib or cop.bib == "":
                et.SubElement(chab, "copyHAB").text = cop.sm
                numhab += 1
        if numhab > 0:
            itn.append(chab)
        if prov != None:
            for cop in self.copies:
                provstr = ";".join(cop.provenances)
                if prov in provstr:
                    oi = et.Element("originalItem")
                    if cop.bib == "":
                        et.SubElement(oi, "institutionOriginal").text = "Herzog August Bibliothek Wolfenbüttel"
                    else:
                        et.SubElement(oi, "institutionOriginal").text = cop.bib                    
                    et.SubElement(oi, "shelfmarkOriginal").text = cop.sm
                    et.SubElement(oi, "provenanceAttribute").text = "; ".join(cop.provenances)
                    itn.append(oi)
                    break                    
        return(itn)

class RecordVD17(Record):
    def __init__(self, node):
        super().__init__(node)    
        try:
            self.vd17 = self.data["006W"]["01"]["0"]
        except:
            self.vd17 = []
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", VD17: " + "|".join(self.vd17) + ", Jahr: " + self.date
        return(ret)
    def to_dict(self):
        res = {
            "ppn" : self.ppn,
            "vdn" : f"VD17 {self.vdn}",
            "permalink" : f"https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%27{self.vdn}%27",
            "recType" : self.get_rec_type(),
            "catRule" : self.catRule,
            "date" : self.date,
            "lang" : ";".join(self.lang),
            "title" : self.title.replace("@", ""),
            "resp" : self.resp,
            "format" : self.format,
            "pages" : self.pages,
            "normPages" : str(self.normPages),
            }
        if self.langOrig != []:
            res["langOrig"] = ";".join(self.langOrig)
        if self.digi != []:
            res["digi"] = ";".join(self.digi)
        if self.gatt != []:
            res["gat"] = ";".join(self.gatt)
        if self.subjects != []:
            res["subjects"] = ";".join(self.subjects)
        if self.persons != []:
            res["persons"] = [pers.to_dict() for pers in self.persons]
        if self.publishers != []:
            res["publishers"] = [pers.to_dict() for pers in self.publishers]
        if self.places != []:
            res["places"] = [pl.to_dict() for pl in self.places]
        if self.copies != []:
            res["copies"] = [cp.to_dict() for cp in self.copies]
        return(res)
    def get_rec_type(self):
        code = self.bbg[0:2]
        conc = { "Aa":"Monographie", "Af":"Teilband", "AF":"Teilband mit eigenem Titel" }
        try:
            return(conc[code])
        except:
            return(self.bbg)
class RecordVD16(Record):
    def __init__(self, node):
        super().__init__(node)    
        try:
            self.vd16 = self.data["006V"]["01"]["0"]
        except:
            self.vd16 = []
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", VD16: " + "|".join(self.vd16) + ", Jahr: " + self.date
        return(ret)
class RecordVD18(Record):
    def __init__(self, node):
        super().__init__(node)    
        try:
            self.vd18 = self.data["006M"]["01"]["0"]
        except:
            self.vd18 = []
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", VD18: " + "|".join(self.vd18) + ", Jahr: " + self.date
        return(ret)        
class RecordInc(Record):
    def __init__(self, node):
        super().__init__(node)
        self.gw = ""
        self.istc = ""
        self.borm = ""
        try:
            bibDict = self.data["009P"]
        except:
            pass
        else:
            for occ in bibDict:
                for link in bibDict[occ]["a"]:
                    if link.find("gesamtkatalog") != -1:
                        self.gw = link
                    elif link.find("istc") != -1:
                        self.istc = link

class Person:
    def __init__(self):
        self.persName = ""
        self.forename = ""
        self.surname = ""
        self.namePart1 = ""
        self.namePart2 = ""
        self.gnd = ""
        self.dateBirth = None
        self.dateDeath = None
    def make_persname(self):
        if self.forename and self.surname:
            self.persName = self.surname + ", " + self.forename
        elif self.namePart1 and self.namePart2:
            self.persName = self.namePart1 + " " + self.namePart2
        elif self.namePart1:
            self.persName = self.namePart1
        elif self.surname:
            self.persName = self.surname
        return(self.persName)
    def __str__(self):
        ret = self.persName
        try:
            ret += " GND: " + self.gnd
        except:
            pass
        return(ret)
    def to_dict(self):
        res = { "persName" : self.persName, "role" : self.role }
        if self.gnd:
            res["gnd"] = self.gnd
        if self.dateBirth:
            res["dateBirth"] = self.dateBirth
        if self.dateDeath:
            res["dateDeath"] = self.dateDeath
        return(res)
    def import_structdata(self, row):
        try:
            self.forename = row["d"].pop(0)
        except:
            pass
        try:
            self.surname = row["a"].pop(0)
        except:
            pass
        try:
            self.namePart1 = row["p"].pop(0)
        except:
            pass
        try:
            self.namePart2 = row["l"].pop(0)
        except:
            pass
        try:
            self.role = row["b"].pop(0)
        except:
            pass
        try:
            self.gnd = row["7"].pop(0).replace("gnd/", "")
        except:
            pass
        try:
            self.dateBirth = row["e"].pop(0)
        except:
            pass
        try:
            self.dateDeath = row["m"].pop(0)
        except:
            pass
        self.make_persname()
        return(True)

class Copy:
    def __init__(self, sm, provenances = [], epn = None):
        self.place = ""
        self.bib = ""
        self.isil = ""
        self.sm = sm
        self.provenances = provenances
        self.epn = epn
    def __str__(self):
        ret = "Signatur: " + self.sm
        if self.isil != "":
            ret = "ISIL: " + self.isil + " " + ret
        if self.provenances != []:
            ret += ", Provenienz: " + ";".join(self.provenances)
        if self.epn != None:
            ret += ", EPN: " + self.epn
        return(ret)
    def get_bib(self):
        bibd = isil.get_bib(self.isil)
        if bibd == False:
            return(False)
        self.bib = bibd["bib"]
        self.place = bibd["place"]
        return(True)
    def to_dict(self):
        self.get_bib()
        ret = {}
        if self.place != "":
            ret["place"] = self.place
        if self.bib != "":
            ret["bib"] = self.bib
        if self.isil != "":
            ret["isil"] = self.isil
        if self.sm != "":
            ret["shelfmark"] = self.sm
        if self.epn != None:
            ret["epn"] = self.epn
        if self.provenances != []:
            ret["provenances"] = ";".join(self.provenances)
        return(ret)

class Place:
    def __init__(self, placeName, rel = None):
        self.placeName = placeName
        self.getty = None
        self.geoNames = None
        self.gnd = None
        self.rel = rel
    def to_dict(self):
        res = { "placeName" : self.placeName }
        if self.getty != None:
            res["getty"] = self.getty
        if self.geoNames != None:
            res["geoNames"] = self.geoNames
        if self.gnd != None:
            res["gnd"] = self.gnd
        if self.rel != None:
            res["relation"] = get_place_relator(self.rel)
        return(res)
        
def assign_mediatype(letter):
    conc = { 
        "A" : "Druck",
        "H" : "Handschrift",
        "K" : "Karte",
        "M" : "Musikalie"
        }
    try:
        return(conc[letter])
    except:
        return("unbekannt")

def get_norm_p(pages):
    normp = 0
    chunks = re.findall(r"(([^BS]+) (Bl)|([^BS]+) (S))", pages)
    for ch in chunks:
        _wh, numbl, _bl, nums, _s = ch
        if numbl != "":
            extrbl = re.findall(r"\d+", numbl)
            for num in extrbl:
                normp += int(num)*2
        elif nums != "":
            extrs = re.findall(r"\d+", nums)
            for num in extrs:
                normp += int(num)
    return(normp)

def recognize_genre(gat):
    genres = ['Adressbuch', 'Agende', 'Akademieschrift', 'Almanach', 'Amtsdruckschrift', 'Anleitung', 'Anstandsliteratur', 'Anthologie', 'Antiquariatskatalog', 'Anzeige', 'Aphorismus', 'Ars moriendi', 'Arzneibuch', 'Atlas', 'Auktionskatalog', 'Autobiographie', 'Ballade', 'Beichtspiegel', 'Bericht', 'Bibel', 'Bibliographie', 'Bibliothekskatalog', 'Biographie', 'Brevier', 'Brief', 'Briefsammlung', 'Briefsteller', 'Buchbinderanweisung', 'Buchhandelskatalog', 'Bücheranzeige', 'Chronik', 'Dissertation', 'Dissertation:theol.', 'Dissertation:phil.', 'Dissertation:med.', 'Dissertation:jur.', 'Dissertationensammlung', 'Drama', 'Edikt', 'Einblattdruck', 'Einführung', 'Elegie', 'Emblembuch', 'Entscheidungssammlung', 'Enzyklopädie', 'Epigramm', 'Epik', 'Epikedeion', 'Epos', 'Erbauungsliteratur', 'Erlebnisbericht', 'ErotischeLiteratur', 'Erzählung', 'Fabel', 'Fallsammlung', 'Fastnachtsspiel', 'Fibel', 'Festbeschreibung', 'Figurengedicht', 'Flugschrift', 'Formularsammlung', 'Frauenliteratur', 'Freimaurerliteratur', 'Führer', 'Fürstenspiegel', 'Gebet', 'Gebetbuch', 'Gelegenheitsschrift', 'Gelegenheitsschrift:Abschied', 'Gelegenheitsschrift:Amtsantritt', 'Gelegenheitsschrift:Begrüßung', 'Gelegenheitsschrift:Einladung', 'Gelegenheitsschrift:Einweihung', 'Gelegenheitsschrift:Fest', 'Gelegenheitsschrift:Friedensschluß', 'Gelegenheitsschrift:Geburt', 'Gelegenheitsschrift:Geburtstag', 'Gelegenheitsschrift:Gedenken', 'Gelegenheitsschrift:Hochzeit', 'Gelegenheitsschrift:Jubiläum', 'Gelegenheitsschrift:Konversion', 'Gelegenheitsschrift:Krönung', 'Gelegenheitsschrift:Namenstag', 'Gelegenheitsschrift:Neujahr', 'Gelegenheitsschrift:Promotion', 'Gelegenheitsschrift:Sieg', 'Gelegenheitsschrift:Taufe', 'Gelegenheitsschrift:Tod', 'Gelegenheitsschrift:Visitation', 'Gesangbuch', 'Gesellschaftsschrift', 'Gesetz', 'Gesetzessammlung', 'Grammatik', 'Handbuch', 'Hausväterliteratur', 'Heiligenvita', 'Hochschulschrift', 'Itinerar', 'Jagdliteratur', 'Jesuitendrama', 'Judaicum', 'Jugendbuch', 'Jugendsachbuch', 'Kalender', 'Kapitulation', 'Karte', 'Katalog', 'Katechismus', 'Kirchenlied', 'Kochbuch', 'Kolportageliteratur', 'Kommentar', 'Kommentar:jur.', 'Kommentar:lit.', 'Kommentar:theol.', 'Kommentar:hist.', 'Kommentar:polit.', 'Komödie', 'Konkordanz', 'Konsiliensammlung', 'Konsilium', 'Legende', 'Leichenpredigt', 'Leichenpredigtsammlung', 'Lesebuch', 'Lexikon', 'Libretto', 'Lied', 'Liedersammlung', 'Lyrik', 'Märchen', 'Märtyrerdrama', 'Mandat', 'Matrikel', 'Meßkatalog', 'Meßrelation', 'Missale', 'Mitgliederverzeichnis', 'Moralische Wochenschrift', 'Musikbuch', 'Musiknoten', 'Musterbuch', 'Novelle', 'Ordensliteratur', 'Ordensliteratur:Augustiner', 'Ordensliteratur:Augustiner-Barfüßer', 'Ordensliteratur:Augustiner-Chorherren', 'Ordensliteratur:Augustiner-Eremiten', 'Ordensliteratur:Barnabiten', 'Ordensliteratur:Benediktiner', 'Ordensliteratur:Chorherren', 'Ordensliteratur:Dominikaner', 'Ordensliteratur:Franziskaner', 'Ordensliteratur:Jesuiten', 'Ordensliteratur:Kapuziner', 'Ordensliteratur:Karmeliter', 'Ordensliteratur:Kartäuser', 'Ordensliteratur:Minimen', 'Ordensliteratur:Minoriten', 'Ordensliteratur:Oratorianer', 'Ordensliteratur:Prämonstratenser', 'Ordensliteratur:Terziaren', 'Ordensliteratur:Theatiner', 'Ordensliteratur:Unbeschuhte Karmeliter', 'Ordensliteratur:Zisterzienser', 'Ornamentstich', 'Ortsverzeichnis', 'Panegyrikos', 'Perioche', 'Pflanzenbuch', 'Pharmakopöe', 'Plan', 'Porträtwerk', 'Praktik', 'Predigt', 'Predigtsammlung', 'Preisschrift', 'Privileg', 'Psalter', 'Ratgeber', 'Rechenbuch', 'Rede', 'Regelsammlung', 'Regesten', 'Reisebericht', 'Reiseführer', 'Rezension', 'Rezensionszeitschrift', 'Richtlinie', 'Rituale', 'Roman', 'Sage', 'Satire', 'Satzung', 'Schäferdichtung', 'Schauspiel', 'Schreibmeisterbuch', 'Schulbuch', 'Schulprogramm', 'Schwank', 'Seuchenschrift', 'Spiel', 'Sprachführer', 'Sprichwortsammlung', 'Streitschrift', 'Streitschrift:polit.', 'Streitschrift:jur.', 'Streitschrift:theol.', 'Subskribentenliste', 'Subskriptionsanzeige', 'Tabelle', 'Tagebuch', 'Theaterzettel', 'Tierbuch', 'Tiermedizin', 'Topographie', 'Totentanz', 'Tragödie', 'Traktat', 'Trivialliteratur', 'Universitätsprogramm', 'Urkundenbuch', 'Verkaufskatalog', 'Verordnung', 'Verserzählung', 'Vertrag', 'Volksbuch', 'Volksschrifttum', 'Vorlesung', 'Vorlesungsverzeichnis', 'Wappenbuch', 'Wörterbuch', 'Zeitschrift', 'Zeitung', 'Zitatensammlung']
    if gat in genres:
        return("genre")
    return(None)
    
def get_place_relator(code):
    conc = {
        "dbp" : "Vertriebsort",
        "prp" : "Entstehungsort",
        "mfp" : "Herstellungsort",
        "pup" : "Erscheinungsort",
        "uvp" : "uvp"
        }
    try:
        return(conc[code])
    except:
        return(code)