#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import json
import logging
import re
import urllib.request as ul
import xml.etree.ElementTree as et
from lib import isil as il
from lib import xmlserializer as xs
from lib import romnumbers as rn
from lib import provenance as prv

class Record:
    def __init__(self):
        self.persons = []
        self.copies = []
        self.places = []
        self.publishers = []
        self.vdn = ""
        self.id = ""
        self.bbg = ""
        self.id_sup = ""
        self.title_sup = ""
        self.vol = ""            
        bud = None
        self.catRule = "rak"
        self.title = ""
        self.resp = ""
        self.edition = ""            
        self.lang = []
        self.langOrig = []
        self.gatt = []
        self.subjects = []
        self.pages = ""
        self.normPages = 0
        self.illustrations = ""
        self.format = ""
        self.date = ""
        self.digi = []
    def __str__(self):
        ret = "record: ID " + self.id + ", Jahr: " + self.date
        return(ret)
    def import_marc(self, node):
        pass
    def to_dict(self):
        res = {
            "id" : self.id,
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
        if self.id_sup != "":
            res["id_sup"] = self.id_sup
            res["title_sup"] = self.title_sup
            res["vol"] = self.vol
        if self.edition != "":
            res["edition"] = self.edition       
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
        et.SubElement(itn, "id").text = "lid" + self.id
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
        idman = self.id
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
    def make_citation(self):
        authors = ", ".join([pers.persName for pers in self.persons if pers.role in ["VerfasserIn", "creator"]])
        places = ", ".join([pl.placeName for pl in self.places])
        publishers = ", ".join([pub.persName for pub in self.publishers])
        ret = self.title
        if authors != "":
            ret = f"{authors}: {ret}"
        try:
            ret = f"{ret}. Teil {self.vol}"
        except:
            pass
        if places != "":
            ret = f"{ret}. {places}"
            if publishers != "":
                ret = f"{ret}: {publishers}"
        if self.date != "":
            ret = f"{ret} {self.date}"
        return(ret)
        
class RecordList():
    def __init__(self, content = None):
        self.content = []
        if content != None:
            for obj in content:
                if isinstance(obj, Record):
                    pass
                else:
                    raise TypeError("Recordlist darf nur Objekte vom Typ Record enthalten")
            self.content = content
    def to_json(self, file_name):
        with open(file_name + ".json", "w", encoding="utf-8") as fp:
            json.dump(self.content, fp, skipkeys=False, ensure_ascii=False, check_circular=True, allow_nan=True, cls=None, indent=1, separators=[',', ':'], default=convert_record, sort_keys=False)
    def to_libreto(self, file_name, metadata, prov = ""):
        ser = xs.Serializer(file_name, "collection")
        ser.add_nested("metadata", metadata)
        for count, rec in enumerate(self.content):
            itemNode = rec.to_libreto(prov)
            ser.add_node(itemNode)
        ser.save()
    
def convert_record(record):
    return(record.to_dict())

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

class Copy:
    def __init__(self):
        self.place = ""
        self.bib = ""
        self.isil = ""
        self.eln = ""
        self.iln = ""
        self.epn = ""
        self.sm = ""
        self.prov = []
        self.prov_struct = []
        self.prov_norm = []
        self.prov_dataset = None
        self.digi = None
    def __str__(self):
        ret = "Signatur: " + self.sm
        if self.isil not in ["", None]:
            ret = "ISIL: " + self.isil + " " + ret
        if self.eln not in ["", None]:
            ret = "ELN: " + self.eln + " " + ret
        if self.iln not in ["", None]:
            ret = "ILN: " + self.iln + " " + ret
        if self.prov not in ["", None, []]:
            ret += ", Provenienz: " + ";".join(self.prov)
        if self.epn not in ["", None, []]:
            ret += ", EPN: " + self.epn
        return(ret)
    def get_bib(self):
        self.isil = il.get_isil(self.iln, "iln")
        if self.isil == None:
            self.isil = il.get_isil(self.eln, "eln")
        bibd = il.get_bib(self.isil, "isil")
        if bibd == None:
            return(None)
        self.bib = bibd["bib"]
        self.place = bibd["place"]
        return(True)       
    def to_dict(self):
        ret = {}
        if self.place != "":
            ret["place"] = self.place
        if self.bib != "":
            ret["bib"] = self.bib
        if self.isil != "":
            ret["isil"] = self.isil
        if self.eln != "":
            ret["eln"] = self.eln
        if self.eln != "":
            ret["iln"] = self.iln            
        if self.sm != "":
            ret["shelfmark"] = self.sm
        if self.epn != None:
            ret["epn"] = self.epn
        if self.prov != []:
            ret["provenances"] = ";".join(self.prov)
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
        
def get_norm_p(pages):
    normp = 0
    chunks = re.findall(r"(([^BS]+) (Bl)|([^BS]+) (S$|S[^p]|Bo)|([^BS]+) Sp)", pages)
    for ch in chunks:
        wh, numbl, _bl, nums, _sbo, numsp = ch
        if "-" in wh:
            continue
        if numbl != "":
            normp += get_number(numbl, 2)
        elif nums != "":
            normp += get_number(nums)
        elif numsp != "":
            normp += get_number(numsp, 0.5)
    chunks2 = re.findall(r"S\.? \d+ ?- ?\d+", pages)
    for ch2 in chunks2:
        normp += get_number(ch2)
    return(normp)
def get_number(page_string, mult=1):
    res = 0
    clean = re.sub(r"[\divxdclmIVXDCLM]+,? \[?(das heißt|i. ?e.)", "", page_string)
    spans = re.findall("(\[?(\d+)\]? ?- ?\[?(\d+)\]?)", clean)
    for span in spans:
        whole, start, end = span
        diff = int(end) - int(start)
        clean = re.sub(whole, str(diff), clean)
    extract = re.findall(r"\d+", clean)
    for num in extract:
        res += int(num)
    extract = re.findall(r"([ivxdclm]+) ", clean.lower())
    for num in extract:
        arab = rn.to_arabic(num)
        if arab == None:
            logging.error(f"Nicht zu parsen: {num}")
        else:
            res += arab
    return(int(res * mult))

def recognize_genre(gat):
    genres = ['Adressbuch', 'Agende', 'Akademieschrift', 'Almanach', 'Amtsdruckschrift', 'Anleitung', 'Anstandsliteratur', 'Anthologie', 'Antiquariatskatalog', 'Anzeige', 'Aphorismus', 'Ars moriendi', 'Arzneibuch', 'Atlas', 'Auktionskatalog', 'Autobiographie', 'Ballade', 'Beichtspiegel', 'Bericht', 'Bibel', 'Bibliographie', 'Bibliothekskatalog', 'Biographie', 'Brevier', 'Brief', 'Briefsammlung', 'Briefsteller', 'Buchbinderanweisung', 'Buchhandelskatalog', 'Bücheranzeige', 'Chronik', 'Dissertation', 'Dissertation:theol.', 'Dissertation:phil.', 'Dissertation:med.', 'Dissertation:jur.', 'Dissertationensammlung', 'Drama', 'Edikt', 'Einblattdruck', 'Einführung', 'Elegie', 'Emblembuch', 'Entscheidungssammlung', 'Enzyklopädie', 'Epigramm', 'Epik', 'Epikedeion', 'Epos', 'Erbauungsliteratur', 'Erlebnisbericht', 'ErotischeLiteratur', 'Erzählung', 'Fabel', 'Fallsammlung', 'Fastnachtsspiel', 'Fibel', 'Festbeschreibung', 'Figurengedicht', 'Flugschrift', 'Formularsammlung', 'Frauenliteratur', 'Freimaurerliteratur', 'Führer', 'Fürstenspiegel', 'Gebet', 'Gebetbuch', 'Gelegenheitsschrift', 'Gelegenheitsschrift:Abschied', 'Gelegenheitsschrift:Amtsantritt', 'Gelegenheitsschrift:Begrüßung', 'Gelegenheitsschrift:Einladung', 'Gelegenheitsschrift:Einweihung', 'Gelegenheitsschrift:Fest', 'Gelegenheitsschrift:Friedensschluß', 'Gelegenheitsschrift:Geburt', 'Gelegenheitsschrift:Geburtstag', 'Gelegenheitsschrift:Gedenken', 'Gelegenheitsschrift:Hochzeit', 'Gelegenheitsschrift:Jubiläum', 'Gelegenheitsschrift:Konversion', 'Gelegenheitsschrift:Krönung', 'Gelegenheitsschrift:Namenstag', 'Gelegenheitsschrift:Neujahr', 'Gelegenheitsschrift:Promotion', 'Gelegenheitsschrift:Sieg', 'Gelegenheitsschrift:Taufe', 'Gelegenheitsschrift:Tod', 'Gelegenheitsschrift:Visitation', 'Gesangbuch', 'Gesellschaftsschrift', 'Gesetz', 'Gesetzessammlung', 'Grammatik', 'Handbuch', 'Hausväterliteratur', 'Heiligenvita', 'Hochschulschrift', 'Itinerar', 'Jagdliteratur', 'Jesuitendrama', 'Judaicum', 'Jugendbuch', 'Jugendsachbuch', 'Kalender', 'Kapitulation', 'Karte', 'Katalog', 'Katechismus', 'Kirchenlied', 'Kochbuch', 'Kolportageliteratur', 'Kommentar', 'Kommentar:jur.', 'Kommentar:lit.', 'Kommentar:theol.', 'Kommentar:hist.', 'Kommentar:polit.', 'Komödie', 'Konkordanz', 'Konsiliensammlung', 'Konsilium', 'Legende', 'Leichenpredigt', 'Leichenpredigtsammlung', 'Lesebuch', 'Lexikon', 'Libretto', 'Lied', 'Liedersammlung', 'Lyrik', 'Märchen', 'Märtyrerdrama', 'Mandat', 'Matrikel', 'Meßkatalog', 'Meßrelation', 'Missale', 'Mitgliederverzeichnis', 'Moralische Wochenschrift', 'Musikbuch', 'Musiknoten', 'Musterbuch', 'Novelle', 'Ordensliteratur', 'Ordensliteratur:Augustiner', 'Ordensliteratur:Augustiner-Barfüßer', 'Ordensliteratur:Augustiner-Chorherren', 'Ordensliteratur:Augustiner-Eremiten', 'Ordensliteratur:Barnabiten', 'Ordensliteratur:Benediktiner', 'Ordensliteratur:Chorherren', 'Ordensliteratur:Dominikaner', 'Ordensliteratur:Franziskaner', 'Ordensliteratur:Jesuiten', 'Ordensliteratur:Kapuziner', 'Ordensliteratur:Karmeliter', 'Ordensliteratur:Kartäuser', 'Ordensliteratur:Minimen', 'Ordensliteratur:Minoriten', 'Ordensliteratur:Oratorianer', 'Ordensliteratur:Prämonstratenser', 'Ordensliteratur:Terziaren', 'Ordensliteratur:Theatiner', 'Ordensliteratur:Unbeschuhte Karmeliter', 'Ordensliteratur:Zisterzienser', 'Ornamentstich', 'Ortsverzeichnis', 'Panegyrikos', 'Perioche', 'Pflanzenbuch', 'Pharmakopöe', 'Plan', 'Porträtwerk', 'Praktik', 'Predigt', 'Predigtsammlung', 'Preisschrift', 'Privileg', 'Psalter', 'Ratgeber', 'Rechenbuch', 'Rede', 'Regelsammlung', 'Regesten', 'Reisebericht', 'Reiseführer', 'Rezension', 'Rezensionszeitschrift', 'Richtlinie', 'Rituale', 'Roman', 'Sage', 'Satire', 'Satzung', 'Schäferdichtung', 'Schauspiel', 'Schreibmeisterbuch', 'Schulbuch', 'Schulprogramm', 'Schwank', 'Seuchenschrift', 'Spiel', 'Sprachführer', 'Sprichwortsammlung', 'Streitschrift', 'Streitschrift:polit.', 'Streitschrift:jur.', 'Streitschrift:theol.', 'Subskribentenliste', 'Subskriptionsanzeige', 'Tabelle', 'Tagebuch', 'Theaterzettel', 'Tierbuch', 'Tiermedizin', 'Topographie', 'Totentanz', 'Tragödie', 'Traktat', 'Trivialliteratur', 'Universitätsprogramm', 'Urkundenbuch', 'Verkaufskatalog', 'Verordnung', 'Verserzählung', 'Vertrag', 'Volksbuch', 'Volksschrifttum', 'Vorlesung', 'Vorlesungsverzeichnis', 'Wappenbuch', 'Wörterbuch', 'Zeitschrift', 'Zeitung', 'Zitatensammlung']
    if gat in genres:
        return("genre")
    return(None)
      
def make_id(name):
    name = name.lower()
    name = name.replace(" ", "_").replace(",", "").replace(".", "")
    name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss").replace("ç", "c").replace("ë", "e")
    return(name)

def get_role(term):
    if term in ["VerfasserIn", "creator", "Verfasser", "Autor"]:
        return("creator")
    return("contributor")