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
    def __init__(self, node):
        self.node = node
        self.data = {}
        self.persons = []
        self.copies = []
        self.places = []
        self.publishers = []
        self.provenances = []
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
        try:
            self.ppn_sup = self.data["036D"]["01"]["9"].pop(0)
        except:
            self.ppn_sup = ""
        try:
            self.title_sup = self.data["036D"]["01"]["a"].pop(0)
        except:
            self.title_sup = ""
        try:
            self.vol = self.data["036D"]["01"]["x"].pop(0)
        except:
            self.vol = ""            
        bud = None
        try:
            bud = self.data["001A"]["01"]["0"].pop(0)
        except:
            pass
        else:
            self.elnRec = bud.split(":").pop(0)
            try:
                self.dateRec = bud.split(":").pop(1)
            except:
                pass
        try:
            self.catRule = self.data["010E"]["01"]["e"].pop(0)
        except:
            self.catRule = "rak"
        self.fingerprint = ""
        self.fingerprint_type = ""
        try:
            self.fingerprint = self.data["007P"]["01"]["0"].pop(0)
            self.fingerprint_type = self.data["007P"]["01"]["s"].pop(0)
        except:
            pass
        if self.fingerprint_type != "fei":
            try:
                self.fingerprint = self.data["007P"]["02"]["0"].pop(0)
                self.fingerprint_type = self.data["007P"]["02"]["s"].pop(0)
            except:
                pass
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
        self.title = self.title.strip(".").replace("@", "")
        try:
            self.title = self.title + ". " + self.data["021A"]["01"]["d"].pop(0)
        except:
            pass
        try:
            self.resp = self.data["021A"]["01"]["h"].pop(0)
        except:
            self.resp = ""
        try:
            self.edition = self.data["032@"]["01"]["a"].pop(0)
        except:
            self.edition = ""            
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
            self.illustrations = self.data["034M"]["01"]["a"].pop(0)
        except:
            self.illustrations = ""
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
        try:
            self.date_end = self.data["011@"]["01"]["b"].pop(0)
        except:
            self.date_end = ""
        self.digi = []
        digi_field = "017D"
        if self.bbg[0:1] == "O":
            digi_field = "017C"
        try:
            digiDict = self.data[digi_field]
        except:
            pass
        else:
            for key in digiDict:
                try:
                    self.digi.extend(digiDict[key]["u"])
                except:
                    pass
        self.comm = []
        self.similar = []
        try:
            commdict = self.data["037A"]
        except:
            pass
        else:
            for key, data in commdict.items():
                for field, content in data.items():
                    if field == "a":
                        self.comm.extend(content)    
        self.load_persons()
        self.load_copies()
        self.load_places()
        self.load_publishers()
        self.load_bib_provenances()
        self.get_vd()
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", Jahr: " + self.date
        return(ret)
    def get_data(self):
        fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield")
        occDict = {}
        for fn in fields:
            tag = fn.get("tag")
            # Das Folgende schließt die Exemplardaten aus, die separat eingelesen werden
            if tag == "101@":
                break
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
    def load_copies(self):
        cp = None
        iln = None
        eln = None
        fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield")
        for fi in fields:
            tag = fi.get("tag")
            # Bei Feld 101@ beginnt eine neue Bibliothek, daher wird die ILN dann in eine Variable gespeichert erforderlich
            if tag == "101@":
                try:
                    iln = get_subfield(fi, "a")
                except:
                    logging.error(f"Fehlende ILN bei PPN {self.ppn}")
            # Dasselbe geschieht bei Feld 202D für die ELN
            if tag == "202D":
                try:
                    eln = get_subfield(fi, "a")
                except:
                    logging.error(f"Fehlende ELN bei PPN {self.ppn}")
            # Bei Feld 203@ beginnt ein neues Exemplar, daher wir das bislang befüllte Exemplar aus der Variable cp in die Liste self.copies verschoben und ein neues angelegt
            # Die zuvor gespeicherten bibliotheksspezifischen Nummern ILN und ELN werden in das neue Objekt geschrieben
            if tag == "203@":
                if cp != None:
                    self.copies.append(cp)
                cp = Copy()
                try:
                    cp.epn = get_subfield(fi, "0")
                except:
                    logging.error(f"Fehlende EPN bei PPN {self.ppn}")
                else:
                    cp.iln = str(iln)
                    cp.eln = str(eln)
                    cp.get_bib()
            # Auslesen der Signatur
            if tag == "209A":
                sm = get_subfield(fi, "a")
                if sm != None and cp.sm == "":
                    cp.sm = sm
                elif sm == None:
                    pass
            # Auslesen des Abrufzeichens in der 8600
            if tag == "209O" and cp.digi == None:
                abl = get_subfield(fi, "a")
                try:
                    cp.abl = abl
                except:
                    logging.info(str(f"Problem mit Abrufzeichen bei {self.ppn}"))
            # Auslesen eines eventuell vorhandenen Digitalisats
            if tag == "209R" and cp.digi == None:
                digi = get_subfield(fi, "u")
                try:
                    cp.digi = digi
                except:
                    logging.info(str(digi))
            # Auslesen der Anmerkungen in 4801
            if tag == "220B":
                comm = get_subfield_list(fi, "a")
                if comm != []:
                    if cp.comm != "":
                        cp.comm = cp.comm + "; "
                    cp.comm = cp.comm + ("; ").join(comm)
            # Auslesen der Bestandsdaten bei Zeitschriften (Ab-Sätze)
            if tag == "231B":
                hist = get_subfield(fi, "a")
                try:
                    cp.holdings = hist
                except:
                    logging.error(f"Fehler beim Auslesen des Erscheinungsverlaufs {cp.sm}");
            if tag == "237A":
                comm = get_subfield_list(fi, "a")
                if comm != []:
                    if cp.comm != "":
                        cp.comm = cp.comm + "; "
                    cp.comm = cp.comm + ("; ").join(comm)
            # Auslesen der Provenienzdaten
            if tag == "244Z":
                provstr = get_subfield(fi, "a")
                codes = get_subfield_list(fi, "x")
                code = ""
                geog = get_subfield(fi, "g")
                if geog not in ["", None]:
                    provstr = f"{provstr}$g{geog}"
                for val in codes:
                    if re.search(r"\d\d", val) != None:
                        code = val
                    else:
                        provstr = f"{provstr}$x{val}"
                ppn = get_subfield(fi, "9")
                bbg = get_subfield(fi, "V")
                if provstr == None:
                    link = prv.NormLinkLocal("Kein Name in XML", ppn, code)
                    link.errors.append("Kein Name in XML. Konversionsfehler?")
                    cp.prov_norm.append(link)
                elif "!" in provstr:
                    link = adjust_xml_244Z(provstr, code)
                    if link != None:
                        cp.prov_norm.append(link)
                elif bbg == None:
                    prov = prv.Provenance(provstr, code)
                    cp.prov_struct.append(prov)
                else:
                    cp.prov_norm.append(prv.NormLinkLocal(provstr, ppn, code))
        # Am Ende des Durchlaufs muss noch das zuletzt angelegte Exemplar in self.copies verschoben werden.
        # Dabei müssen eventuell noch verbleibende Provenienzdaten angehängt werden (warum?)
        if cp != None:
            if cp.prov_struct != [] or cp.prov_norm != []:
                cp.prov_dataset = prv.Dataset(cp.epn, cp.prov_struct, cp.prov_norm)
            self.copies.append(cp)
    def get_sdd_sys(self):
        ret = []
        fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield")
        sdd_not = []
        for fi in fields:
            tag = fi.get("tag")
            if tag == "145Z":
                sdd_not = get_subfield_list(fi, "a")
        return(";".join(sdd_not))
    def get_local_sys(self, isil):
        ret = []
        fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield")
        if isil == "1":
            regex = re.compile(r"[A-Z][a-z] [0-9]+")
            for fi in fields:
                tag = fi.get("tag")
                if tag == "145S":
                    notations = get_subfield_list(fi, "a")
                    if notations != []:
                        ret.extend(notations)
        if isil == "7":
            regex = re.compile(r"[A-Z ]+\.[0-9]{3}")
            for fi in fields:
                tag = fi.get("tag")
                if tag == "245Z":
                    notations = get_subfield_list(fi, "a")
                    if notations != []:
                        ret.extend(notations)        
        if isil == "23":
            regex = re.compile(r"[A-Z]+ [A-Z][a-z]")
            for fi in fields:
                tag = fi.get("tag")
                if tag == "145Z":
                    notations = get_subfield_list(fi, "a")
                    if notations != []:
                        ret.extend(notations)
        if ret != []:
            ret = [sys for sys in ret if regex.match(sys)]
            return(list(ret))
        return(ret)
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
            place = Place(placeName, placeRel)
            try:
                expansion = placeList[occ]["7"].pop(0)
                place.gnd = re.search("gnd/([\d\-]{7,12})", expansion).group(1)
            except:
                pass
            self.places.append(place)
    def get_ill_information(self):
        type_strings = ["ill", "kupferst", "holzschn", "portr", "abb", "frontisp", "kupfert", "kt", "karte", "falttaf", "druckerm", "graph"]
        regex_quant = f"(\d+)\]?\s({'|'.join(type_strings)})"
        self.num_ill = 0
        self.types_ill = set()
        if self.illustrations == "":
            return(0)
        elements = [el.strip().lower() for el in self.illustrations.split(",")]
        for el in elements:
            extr = re.search(f"(.+)\s\((.+)\)", el)
            if extr == None:
                for ts in type_strings:
                    if ts in el:
                        self.types_ill.add(ts)
                continue
            for ts in type_strings:
                if ts in extr.group(2):
                    self.types_ill.add(ts)
        for el in elements:
            extr_quant = re.search(r"\d+", el)
            try:
                self.num_ill += int(extr_quant.group(0))
            except:
                self.num_ill += 1
        return(self.num_ill)
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
    def load_bib_provenances(self):
        try:
            prov_data = self.data["092B"]
        except:
            return(None)
        for key, row in prov_data.items():
            provenance = prv.ProvenanceBibLevel()
            try:
                provenance.isil = row["5"].pop(0)
            except:
                pass
                #logging.error(f"Provenienz ohne ISIL in {self.ppn}")
            try:
                provenance.epn = row["2"].pop(0)
            except:
                pass
                #logging.error(f"Provenienz ohne EPN in {self.ppn}")
            try:
                provenance.sm = row["3"].pop(0)
            except:
                pass
                #logging.error(f"Provenienz ohne Signatur in {self.ppn}")
            try:
                provenance.name = row["a"].pop(0)
            except:
                pass                
            try:
                provenance.date = row["c"].pop(0)
            except:
                pass
            try:
                provenance.descriptors = row["b"]
            except:
                pass
            try:
                provenance.ppn = row["9"].pop(0)
            except:
                pass
            try:
                provenance.gnd = row["7"].pop(0)
            except:
                pass               
            try:
                provenance.comment = row["k"].pop(0)
            except:
                pass    
            self.provenances.append(provenance)
        for cp in self.copies:
            cp.prov_bib = list(filter(lambda p: p if p.epn == cp.epn else None, self.provenances))
    def get_vd(self):
        if self.bbg[0] == "O":
            try:
                bib_refs = self.data["007S"]
            except:
                pass
            else:
                for key, val in bib_refs.items():
                    text = val["0"].pop(0)
                    if "VD1" in text:
                        self.vdn = text
                        return
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
    def get_sm(self, epn):
        for cp in self.copies:
            if cp.epn == epn:
                return(cp.sm)
        return(None)       
    def get_rec_type(self):
        code = self.bbg[0:2]
        conc = { "Aa":"Monographie", "Af":"Teilband", "AF":"Teilband mit eigenem Titel" }
        try:
            return(conc[code])
        except:
            return(self.bbg)    
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
        if self.ppn_sup != "":
            res["ppn_sup"] = self.ppn_sup
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
    def to_libreto(self, gdb, prov = None):
        itn = et.Element("item")
        et.SubElement(itn, "id").text = "lid" + self.ppn
        et.SubElement(itn, "titleBib").text = self.title
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
                if gdb != None:
                    gdata = gdb.get_dict(pl.placeName)
                    try:
                        et.SubElement(placen, "getty").text = gdata["getty"]
                    except:
                        pass
                    try:
                        lat = gdata["lat"]
                        long = gdata["long"]
                    except:
                        pass
                    else:
                        gdel = et.Element("geoData")
                        et.SubElement(gdel, "lat").text = gdata["lat"]
                        et.SubElement(gdel, "long").text = gdata["long"]
                        placen.append(gdel)
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
        if self.langOrig != []:
            langl = et.Element("languagesOriginal")
            for code in self.lang:
                et.SubElement(langl, "languageOriginal").text = code
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
        
    def to_libreto_copies(self, gdb, no):
        itn = et.Element("item")
        et.SubElement(itn, "id").text = "lid" + self.ppn
        et.SubElement(itn, "titleBib").text = self.title
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
                if gdb != None:
                    gdata = gdb.get_dict(pl.placeName)
                    try:
                        et.SubElement(placen, "getty").text = gdata["getty"]
                    except:
                        pass
                    try:
                        lat = gdata["lat"]
                        long = gdata["long"]
                    except:
                        pass
                    else:
                        gdel = et.Element("geoData")
                        et.SubElement(gdel, "lat").text = gdata["lat"]
                        et.SubElement(gdel, "long").text = gdata["long"]
                        placen.append(gdel)
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
        if self.langOrig != []:
            langl = et.Element("languagesOriginal")
            for code in self.lang:
                et.SubElement(langl, "languageOriginal").text = code
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
        oi = et.Element("originalItem")
        cop = self.copies[no]
        if cop.bib == "":
            et.SubElement(oi, "institutionOriginal").text = "Herzog August Bibliothek Wolfenbüttel"
        else:
            et.SubElement(oi, "institutionOriginal").text = cop.bib                    
        et.SubElement(oi, "shelfmarkOriginal").text = cop.sm
        try:
            et.SubElement(oi, "provenanceAttribute").text = "; ".join(cop.provenances)
        except:
            pass
        itn.append(oi)                  
        return(itn)        
        
    def to_json(self):
        ret = json.dumps(self.to_dict(), ensure_ascii=False)
        return(ret)
    def make_citation(self):
        authors = ", ".join([pers.persName for pers in self.persons if pers.role in ["VerfasserIn", "creator"]])
        places = ", ".join([pl.placeName for pl in self.places])
        publishers = ", ".join([pub.persName for pub in self.publishers])
        ret = self.title.strip(".")
        if self.edition:
            ret = f"{ret}. {self.edition.strip('.')}"
        if authors != "":
            ret = f"{authors}: {ret}"
        if self.vol:
            ret = f"{ret}. Teil {self.vol}"
        if places != "":
            ret = f"{ret}. {places}"
            if publishers != "":
                ret = f"{ret}: {publishers}"
        if self.date != "":
            ret = f"{ret} {self.date}"
        return(ret)
    def get_reservation(self):
        ret = []
        try:
            resdict = self.data["046X"]
        except:
            return(ret)
        for occ, data in resdict.items():
            reservation = { "status" : "", "date" : "", "isil" : "", "note" : "", "digitalisierbar" : "" }
            try:
                reservation["status"] = data["a"].pop()
            except:
                pass
            try:
                reservation["date"] = data["c"].pop()
            except:
                pass
            try:
                reservation["isil"] = data["5"].pop()
            except:
                pass
            try:
                reservation["note"] = data["z"].pop()
            except:
                pass
            if "HAB" in reservation["note"] and reservation["isil"] == "":
                reservation["isil"] = "DE-23"
            reservation["digitalisierbar"] = reservation["status"].replace("cc", "Nein").replace("cb", "Ja")
            ret.append(reservation)
        return(ret)

class RecordVD17(Record):
    def __init__(self, node):
        super().__init__(node)    
        try:
            self.vd17 = self.data["006W"]["01"]["0"]
        except:
            self.vd17 = []
        for com in self.comm:
            if "Nicht identisch mit VD" in com:
                extr = re.search(r"mit VD ?17 ([0-9]+:[^ ]+)", com)
                try:
                    self.similar.append(extr.group(1))
                except:
                    pass
        if self.digi == []:
            try:
                vtind = self.data["017E"]["01"]["5"][0]
            except:
                pass
            else:
                if vtind == "34":
                    self.digi.append("https://vd17.gbv.de/vd/vd17/" + self.vdn.replace("VD17 ", ""))
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", VD17: " + self.vdn + ", Jahr: " + self.date
        return(ret)
    def to_dict(self):
        res = {
            "ppn" : self.ppn,
            "vdn" : f"VD17 {self.vdn}",
            "permalink" : f"https://kxp.k10plus.de/DB=1.28/CMD?ACT=SRCHA&IKT=8079&TRM=%27{self.vdn}%27",
            "bbg" : self.bbg,
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
        if self.ppn_sup != "":
            res["ppn_sup"] = self.ppn_sup
            res["title_sup"] = self.title_sup
            res["vol"] = self.vol
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
    def load_copies(self):
        cp = None
        iln = None
        eln = None
        fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield")
        for fi in fields:
            tag = fi.get("tag")
            if tag == "101@":
                try:
                    iln = get_subfield(fi, "a")
                except:
                    logging.error(f"Fehlende ILN bei PPN {self.ppn}")
            if tag == "202D":
                try:
                    eln = get_subfield(fi, "a")
                except:
                    logging.error(f"Fehlende ELN bei PPN {self.ppn}")
            if tag == "203@":
                if cp != None:
                    self.copies.append(cp)
                cp = Copy()
                try:
                    cp.epn = get_subfield(fi, "0")
                except:
                    logging.error(f"Fehlende EPN bei PPN {self.ppn}")
                else:
                    cp.iln = str(iln)
                    cp.eln = str(eln)
                    cp.get_bib()
            if tag == "209A":
                sm = get_subfield(fi, "a")
                if sm != None and cp.sm == "":
                    cp.sm = sm
                elif sm == None:
                    pass
            if tag == "209R" and cp.digi == None:
                digi = get_subfield(fi, "u")
                try:
                    cp.digi = digi
                except:
                    logging.info(str(digi))
            if tag == "244Z":
                provstr = get_subfield(fi, "a")
                codes = get_subfield_list(fi, "x")
                code = ""
                for val in codes:
                    if re.search(r"\d\d", val) != None:
                        code = val
                ppn = get_subfield(fi, "9")
                bbg = get_subfield(fi, "V")
                # if provstr == None and ppn != None and code != "":
                if provstr == None:
                    link = prv.NormLinkLocal("Kein Name in XML", ppn, code)
                    link.errors.append("Kein Name in XML. Konversionsfehler?")
                    cp.prov_norm.append(link)
                elif "!" in provstr:
                    link = adjust_xml_244Z(provstr, code)
                    if link != None:
                        cp.prov_norm.append(link)
                elif bbg == None:
                    prov = prv.Provenance(provstr, code)
                    cp.prov_struct.append(prov)
                else:
                    cp.prov_norm.append(prv.NormLinkLocal(provstr, ppn, code))
        if cp != None:
            if cp.prov_struct != [] or cp.prov_norm != []:
                cp.prov_dataset = prv.Dataset(cp.epn, cp.prov_struct, cp.prov_norm)
            self.copies.append(cp)

class RecordVD16(Record):
    def __init__(self, node):
        super().__init__(node)
        try:
            self.vd16 = self.data["006V"]["01"]["0"]
        except:
            try:
                self.vd16 = self.data["007S"]["01"]["0"]
            except:
               self.vd16 = []
        self.vdn = ";".join(self.vd16)
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", VD16: " + "|".join(self.vd16) + ", Jahr: " + self.date
        return(ret)
    def load_places(self):
        try:
            placeList = self.data["029F"]
        except:
            return(None)
        for occ in placeList:
            try:
                placeName = placeList[occ]["a"].pop(0)
            except:
                continue
            placeName = re.sub("\!.+\!", "", placeName)
            self.places.append(Place(placeName, "Druck- oder Erscheinungsort"))
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
            try:
                placePPN = placeList[occ]["9"].pop(0)
            except:
                placePPN = ""                
            placeName = re.sub("\!.+\!", "", placeName)
            self.places.append(Place(placeName, placeRel))            
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
class RecordZS(Record):
    def __init__(self, node):
        super().__init__(node)
        self.mediatype = "keine Angabe"
        try:
            mtd = [val["a"].pop(0) for key, val in self.data["002E"].items()]
        except:
            pass
        else:
            self.mediatype = ";".join(mtd)
        try:
            self.serial_type = self.data["013D"]["01"]["a"].pop(0)
        except:
            self.serial_type = "Zeitschrift oder Zeitung"
        self.ppn_repr = ""
        self.zdb_repr = ""       
        try:
            self.zdb = self.data["007G"]["01"]["0"].pop(0)
        except:
            self.zdb = ""
        try:
            self.country = self.data["019@"]["01"]["a"].pop(0)
        except:
            self.country = ""            
        try:
            sys_repr = self.data["039I"]["01"]["c"]
            ids_repr = self.data["039I"]["01"]["6"]
            self.ids_repr = dict(zip(sys_repr, ids_repr))
            try:
                self.ppn_repr = self.ids_repr["KXP"]
            except:
                pass
            try:
                self.zdb_repr = self.ids_repr["ZDB"]
            except:
                pass              
        except:
            pass
        try:
            self.pub_hist_rough = self.data["031@"]["01"]["a"].pop(0)
        except:
            pass
        try:
            self.pub_hist_bibl = PublishingHistory(self.data["031N"]["01"])
        except:
            pass

class RecordRISM(Record):
    def __init__(self, node):
        super().__init__(node)
        self.rism = []
        try:
            bibref_data = self.data["007S"]
        except:
            pass
        else:
            for key1, data1 in bibref_data.items():
                for key2, val_list in data1.items():
                    for val in val_list:
                        if "RISM" in val:
                            self.rism.append(val)

class PublishingHistory():
    def __init__(self, fieldDict = None, type = None):
        self.type = "general"
        if type == "local":
            self.type = "local"
        self.start = { "year" : 0, "volume" : 0, "issue" : 0 }
        self.end = { "year" : 0, "volume" : 0, "issue" : 0 }
        self.complete = True
        if isinstance(fieldDict, dict):
            try:
                self.start["year"] = int(fieldDict["j"].pop(0))
            except:
                pass
            try:
                self.start["volume"] = int(fieldDict["d"].pop(0))
            except:
                pass
            try:
                self.end["year"] = int(fieldDict["n"].pop(0))
            except:
                pass
            try:
                self.end["volume"] = int(fieldDict["k"].pop(0))
            except:
                pass        

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
    def to_libreto(self, file_name, metadata, prov = None, gdb = None):
        ser = xs.Serializer(file_name, "collection")
        ser.add_nested("metadata", metadata)
        for count, rec in enumerate(self.content):
            itemNode = rec.to_libreto(gdb, prov)
            ser.add_node(itemNode)
        path = ser.save()
        return(path)
        
    def to_libreto_copies(self, file_name, metadata, gdb):
        ser = xs.Serializer(file_name, "collection")
        ser.add_nested("metadata", metadata)
        for rec in self.content:
            for no, cop in enumerate(rec.copies):
                itemNode = rec.to_libreto_copies(gdb, no)
                ser.add_node(itemNode)
        path = ser.save()
        return(path)        
        
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
    def __init__(self):
        self.place = ""
        self.bib = ""
        self.isil = ""
        self.eln = ""
        self.iln = ""
        self.epn = ""
        self.sm = ""
        self.comm = ""
        self.prov_bib = []
        self.prov = []
        self.prov_struct = []
        self.prov_norm = []
        self.prov_dataset = None
        self.digi = None
        self.abl = ""
        # Nur für Zeitschriftenexemplarsätze
        self.holdings = ""
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
    def get_prov_names(self):
        if self.prov_struct == []:
            return("")
        return(";".join([prov.name for prov in self.prov_struct]))
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
        self.ppn = None
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
    extract = re.findall(r"^([ivxdclm]+)$", clean.lower())
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

def get_subfield(node, code):
    code = code.lower()
    children = node.findall("*")
    for ch in children:
        retcode = ch.get("code").lower()
        if code == retcode:
            return(ch.text)
    return(None)

def get_subfield_list(node, code):
    ret = []
    code = code.lower()
    children = node.findall("*")
    for ch in children:
        try:
            retcode = ch.get("code").lower()
        except:
            pass
        else:
            if code == retcode:
                ret.append(ch.text)
    return(ret)
    
def adjust_xml_244Z(provstr, code):
    # !345231570!|k|Kloster zur Ehre Gottes <Salzdahlum>
    search = re.search("\!([\dX]+)\!(\|[pk]\|)?([^!]+)", provstr)
    if search == None:
        return(None)
    link = prv.NormLinkLocal(search.group(3), search.group(1), code)
    return(link)
    
def make_id(name):
    name = name.lower()
    name = name.replace(" ", "_").replace(",", "").replace(".", "")
    name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss").replace("ç", "c").replace("ë", "e")
    return(name)

def get_role(term):
    if term in ["VerfasserIn", "creator", "Verfasser", "Autor"]:
        return("creator")
    return("contributor")
    
def refine_place(name):
    name = name.replace("[?]", "")
    name = name.replace("(?)", "")    
    name = name.strip("?")
    name = name.strip("[]")
    name = name.strip()
    repl = {
        "!006931979e" : "Erfurt",
        "Altdorf b. Nürnberg" : "Altdorf",
        "ALtenburg" : "Altenburg",
        "Altenburg/Thüringen" : "Altenburg",
        "Altenburg$gThüringen" : "Altenburg",
        "Beyreuth" : "Bayreuth",
        "Brandenburg <Havel>" : "Brandenburg an der Havel",
        "Brandenburg" : "Brandenburg an der Havel",
        "Bytom Odrzański" : "Beuthen an der Oder",
        "Clausthal" : "Clausthal-Zellerfeld",
        "Dortmundt" : "Dortmund",
        "Dillingen a. d. Donau" : "Dillingen an der Donau",
        "Dillingen a.d. Donau" : "Dillingen an der Donau",
        "leipzig" : "Leipzig",
        "Frankfurt" : "Frankfurt am Main",
        "Frankfurt, Main" : "Frankfurt am Main",
        "Frankfurt, Oder" : "Frankfurt (Oder)",
        "FReiberg" : "Freiberg",
        "Freiburg, Breisgau" : "Freiburg im Breisgau",
        "Giessen" : "Gießen",
        "Grossenhain" : "Großenhain",
        "Halberstedt" : "Halberstadt",
        "Halle" : "Halle (Saale)",
        "Halle, Saale" : "Halle (Saale)",
        "Hof / Saale" : "Hof (Saale)",
        "Hof <Oberfranken>" : "Hof (Saale)",
        "Iena" : "Jena",
        "Jawor" : "Jauer",
        "Köngisberg" : "Königsberg",
        "Lauingen, Donau" : "Lauingen (Donau)",
        "Minden (Westf)" : "Minden",
        "Münster (Westf)" : "Münster",
        "Neuburg, Donau" : "Neuburg an der Donau",
        "Neustadt, Aisch" : "Neustadt an der Aisch",
        "Neustadt, Weinstraße" : "Neustadt an der Weinstraße",
        "Nysa" : "Neiße",
        "Oettingen i. Bay." : "Oettingen in Bayern",
        "Oettingen" : "Oettingen in Bayern",
        "Rothenburg <Tauber>" : "Rothenburg ob der Tauber",
        "Statthagen" : "Stadthagen",
        "Stargard Szczeciński" : "Stargard in Pommern",
        "Steinau, Oder" : "Steinau an der Oder",
        "Strassburg" : "Straßburg",
        "Sulzbach$gOberpfalz" : "Sulzbach",
        "Weißenfels <Halle, Saale>" : "Weißenfels",
        "Weissenfels" : "Weißenfels",
        "Zerbst/Anhalt" : "Zerbst"
        }
    try:
        name = repl[name]
    except:
        pass
    return(name)    
