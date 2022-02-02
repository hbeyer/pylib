#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import urllib.request as ul
import xml.etree.ElementTree as et
import re

class Record:
    def __init__(self, node):
        self.node = node
        self.data = {}
        self.persons = []
        self.copies = []
        self.places = []
        self.publishers = []
        self.getData()        
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
        # Funktioniert igendwie nicht
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
            self.getNormP()
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
        self.loadPersons()
        self.loadCopies()
        self.loadPlaces()
        self.loadPublishers()
    def __str__(self):
        ret = "record: PPN " + self.ppn + ", Jahr: " + self.date
        return(ret)
    def getData(self):
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
    def loadPersons(self):
        try:
            creatorList = self.data["028A"]
        except:
            pass
        else:
            for occ in creatorList:
                per = Person()
                per.role = "creator"
                per.importStructData(creatorList[occ])
                self.persons.append(per)
        try:
            creatorList2 = self.data["028B"]
        except:
            pass
        else:
            for occ in creatorList2:
                per = Person()
                per.role = "creator"
                per.importStructData(creatorList2[occ])
                self.persons.append(per)
        try:
            contributorList = self.data["028C"]
        except:
            pass
        else:
            for occ in contributorList:
                per = Person()
                per.role = "contributor"
                per.importStructData(contributorList[occ])
                self.persons.append(per)            
    def loadCopies(self):
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
    def loadPlaces(self):
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
            self.places.append(Place(placeName, placeRel))
    def loadPublishers(self):
        try:
            pubRow = self.data["033J"]
        except:
            return(None)
        for occ in pubRow:
            pub = Person()
            pub.role = "publisher"
            pub.importStructData(pubRow[occ])
            self.publishers.append(pub)
    def getNormP(self):
        if self.catRule == "rda":
            extract = re.findall(r"(\d+) (ungezählte )?Seiten", self.pages)
            for group in extract:
                self.normPages += int(group[0])
            extract = re.findall(r"(\d+) (ungezählte |ungezähltes )?Bl[äa]tt", self.pages)
            for group in extract:
                self.normPages += int(group[0])*2
            extract = re.findall(r"(\d+) B[oö]gen", self.pages)
            for group in extract:
                self.normPages += int(group)*2                
            return(True)
        else:
            extract = re.findall(r"(\d+) S\.?", self.pages)
            for group in extract:
                self.normPages += int(group)
            extract = re.findall(r"\[?(\d+)\]? Bl\.?", self.pages)
            for group in extract:
                self.normPages += int(group)*2
        return(True)

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
    def makePersName(self):
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
    def importStructData(self, row):
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
        self.makePersName()
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

class Place:
    def __init__(self, placeName, rel = None):
        self.placeName = placeName
        self.getty = None
        self.geoNames = None
        self.gnd = None
        self.rel = rel