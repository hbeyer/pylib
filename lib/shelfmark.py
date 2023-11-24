#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import logging

class Shelfmark:
    def __init__(self, whole):
        self.whole = whole.strip()
        self.root = ""
        self.bareRoot = ""
        self.collection = ""
        self.part = ""
        self.group = ""
        self.form = ""
        self.number = ""
        self.format = ""
        self.volume = ""        
        self.valid = False        
        rexx = {
            "A:" : "A",
            "Theol|Jur|Hist|Bell|Pol|Oec|Eth|Med|Geog|Astr|Phys|Geom|Arit|Poet|Log|Rhet|Gram|Quod" : "A",
            "Helmst\. Dr" : "HHD",
            "Helmst" : "H",
            "QuH" : "HQU",
            "QuN" : "MQN",
            "Music" : "MMU",
            "M:" : "M",
            "Schulenb" : "YSL",
            "([ABCDEFGHJKLMNOPRSTUVZ][a-z]|QuN) " : "M",
            "Bibel-S\." : "BS",
            "(ae|Ä)ltere [Ee]inblattdrucke" : "AEB",
            "^I[A-Z] [0-9]" : "AEC",
            "Alv\." : "ALV",
            "Xylogr" : "XYL",
            "Druckfragm" : "FGM",
            "[WX][a-z] " : "NE",
            "Eyssen" : "YEY",
            "Kranz" : "YKR",
            "Kreuder" : "YKD",
            "Ars libr" : "YMA",
            "Maler" : "YMM",
            "Stolb" : "YST",
            "Textb" : "YTM",
            "Töpfer" : "YTO",
            "Zapf" : "YHZ",
            "G[123]" : "YGG",
            "R[1234]:" : "YRA",
            "Dep\." : "YXD",
            "Aug\.|Novi|Extrav|Cod\.|Blank" : "ZHA",
            "BA [IV]" : "ZHB",            
            "Graph" : "ZGR",
            "^K [0-9]" : "ZKA",
            "^1?\d{2}\.(2°|4°|8°|12°) \d{1,6}" : "ZNS",
            "^1?\d{2}\.\d{1,6}" : "ZNC",
            "[A-Z][A-Z] \d{2}-\d{4}" : "ZPB"
            }
        for rex, val in rexx.items():
            if re.search(rex, self.whole) != None:
                self.collection = val
                break
        if "Slg. Hardt" in self.whole:
            self.root = "M: Li 5530"
            self.bareRoot = "Li 5530"
            extract = re.search(r"\(\d+,\s?(\d+[a-z]?)((, \(?(\d+)\d?))?\)$", self.whole)
            try:
                self.part = extract.group(1)
            except:
                logging.error("Problem bei " + self.whole)
        else:
            extract = re.search(r"(.+)\s\(([0-9]+[\.,]?[a-dIV]{0,3})\)$", self.whole)
            #extract = re.search(r"(.+)\s\(([0-9a-dIV]{1,3})\)$", self.whole)
            try:
                self.part = extract.group(2)                
            except:
                pass
            try:
                self.root = extract.group(1)
            except:
                self.root = self.whole
            if self.collection == "AEB":
                self.root = self.root.replace("aelt", "Ält")
                self.root = self.root.replace("einbl", "Einbl")
            if self.collection in ["A", "H", "M"]:
                self.bareRoot = self.root.replace(self.collection + ": ", "")
            else:
                self.bareRoot = self.root
        if self.collection and self.root:
            self.valid = True
    def __str__(self):
        ret = self.root
        if self.part:
            ret += ' (' + self.part + ')'
        return(ret)
    def normalize_wdb(self):
        norm_sig = self.whole.replace("A: ", "").replace("H: ", "").replace("M: ", "")
        norm_sig = norm_sig.replace("Helmst.", "helmst")
        norm_sig = norm_sig.replace("°", "f")
        norm_sig = lower(norm_sig)
        #norm_sig = re.replace(r"\((\d+)\)", norm_sig, )
        return(norm_sig)
    def getFormat(self):
        extract = re.search(r"2°|4°|8°|12°|16°|FM", self.whole)
        try:
            self.format = extract.group(0)
        except:
            return(None)
        else:
            return(self.format)
    def getGroup(self):
        if self.collection == "A":
            extract = re.search(r"Theol|Jur|Hist|Bell|Pol|Oec|Eth|Med|Geogr|Astr|Phys|Geom|Arit|Poet|Log|Rhet|Gram|Quod", self.whole)
            conc = {"Gram":"Gramm", "Arit":"Arith", "Astr":"Astron"}
            try:
                self.group = extract.group(0)
            except:
                return(None)
            try:
                self.group = conc[self.group]
            except:
                pass
            self.group = self.group + "."
        elif self.collection == "M":
            extract = re.search(r"[ABCDEFGHJKLMNOPQRSTUVZ][a-z]N?", self.whole)
            try:
                self.group = extract.group(0)
            except:
                return(None)
        elif self.collection == "H":
            extract = re.search(r"\s?([A-Z]|Y[a-z])\s", self.whole)
            try:
                self.group = extract.group(1)
            except:
                return(None)
        elif self.collection == "YGG":
            extract = re.search(r"([123]):([A-Z])(\d+)", self.whole)
            try:
                self.group = extract.group(1) + extract.group(2)
            except:
                return(None)
            try:
                self.number = extract.group(3)
            except:
                return(None)
        elif self.collection == "YRA":
            extract = re.search(r"R([123])", self.whole)
            try:
                self.group = extract.group(1).zfill(6)
            except:
                return(None)
        elif self.collection == "ZPB":
            extract = re.search(r"([A-Z][A-Z]) (\d{2})-", self.whole)
            try:
                self.group = extract.group(1) + extract.group(2).zfill(4)
            except:
                return(None)
        else:
            extract = re.search(r"([A-Z][a-z])\s", self.whole)
            try:
                self.group = extract.group(1)
            except:
                return(None)            
        return(self.group)
    def getForm(self):
        extract = re.search(r"Sammelb|Mischb|Kapsel|Sammelma", self.whole)
        conc = { "Sammelb":"Sammelbd.", "Mischb":"Mischbd.", "Kapsel":"Kapsel", "Sammelma":"Sammelmappe" }
        try:
            self.form = conc[extract.group(0)]
        except:
            pass
        return(self.form)
    def getNumber(self):
        if self.collection == "H":
            extract = re.search(r"(H: )?([A-Z]|Y[a-z])\s([0-9]+[a-z]{0,2}\*?)\.?(2°|4°|8°|12°)?", self.whole)
            try:
                self.number = extract.group(3)
            except:
                extract = re.search(r"H:\sQuH\s([0-9]+\.?([0-9]+)?)", self.whole)
                try:
                    self.number = extract.group(2)
                except:
                    return(None)
        elif self.collection == "A":
            extract = re.search(r"([0-9\.-a-z]+)\s[A-Z][a-z]+\.", self.whole)
            #extract = re.search(r"A: ([0-9\.-a-z]+)\s[A-Z][a-z]+\.", self.whole)
            try:
                self.number = extract.group(1)
            except:
                 return(None)
        elif self.collection == "M":
            extract = re.search(r"(M: )?([A-Z][a-z]|QuN)\s((gr\.-2°|2°|4°|8°|12°)\s)?((Mischbd\.|Sammelbd\.|Kapsel)\s)?([0-9\.]+)", self.whole)
            try:
                self.number = extract.group(7)
            except:
                return(None)
        elif self.collection == "XYL":
            extract = re.search(r"([0-9]+)\sXyl", self.whole)
            try:
                self.number = extract.group(1)
            except:
                return(None)
        elif self.collection == "AEB":
            extract = re.search(r"drucke\s([0-9]+)", self.whole)
            try:
                self.number = extract.group(1)
            except:
                return(None)
        elif self.collection == "NE":
            extract = re.search(r"[WX][a-z]( 2°|4°|8°|12°)? ([0-9\.]+)", self.whole)
            try:
                self.number = extract.group(2)
            except:
                if "FM" in self.whole:
                    extract = re.search(r"FM (\d+)", self.whole)
                    try:
                        self.number = extract.group(1)
                    except:
                        return(None)
        elif self.collection == "ZNC":
            extract = re.search(r"(\d+\.\d+)", self.whole)
            try:
                self.number = extract.group(1)
            except:
                return(None)
        elif self.collection == "ZNS":
            extract = re.search(r"(\d+)\.1?[248]° (\d+)", self.whole)
            #extract = re.search(r"(\d+)\.1?[248]°\s\(d+)", self.whole)
            try:
                self.number = f"{extract.group(1)}.{extract.group(2)}"
            except:
                return(None)         
        elif self.collection == "ZPB":
            extract = re.search(r"-(\d{4})?", self.whole)
            try:
                self.number = extract.group(1)
            except:
                return(None)
        else:
            extract = re.search(r"\s([0-9\.]+[a-z]?)[^°\d]", self.whole)
            try:
                self.number = extract.group(1)
            except:
                extract = re.search(r"\s([0-9\.]+[a-z]?)$", self.whole)
                try:
                    self.number = extract.group(1)
                except:
                    return(None)
        return(self.number)
    def getVolumeNo(self):
        extract = re.search(r":([0-9\.-]{1,4})", self.whole)
        try:
            self.volume = extract.group(1)
        except:
            pass
class StructuredShelfmark(Shelfmark):
        def __init__(self, whole):
            super().__init__(whole)            
            self.getFormat()
            self.getGroup()
            self.getForm()
            self.getNumber()
            self.getVolumeNo()
            self.sortable = self.makeSortable()
        def __str__(self):
            ret = "Bestand: " + self.collection
            if self.group != "":
                ret = ret + ", Klasse: " + self.group
            ret = ret + ", Nummer: " + self.number
            if self.format:
                ret = ret + ", Format: " + self.format
            if self.part:
                ret = ret + ", Stücktitel: " + self.part
            return(ret)
        def sortableNum(self, num):
            parts = num.split(".")
            parts = self.separateLetters(parts)
            parts = [p.zfill(5) for p in parts]
            diff = 5 - len(parts)
            for num in range(0, diff):
                parts.append("00000")
            return(".".join(parts))
        def separateLetters(self, parts):
            ret = []
            for p in parts:
                extract = re.search(r"([0-9]+)([a-z]+)", p)
                try:
                    sp = [extract.group(1), extract.group(2)]
                except:
                    sp = [p]
                ret.extend(sp)
            return(ret)
        def translateGroup(self):
            if self.collection != "A":
                return(self.group)
            conc = {
                "Theol.":"01Theo",
                "Jur.":"02Jur",
                "Hist.":"03Hist",
                "Bell.":"04Bell",
                "Pol.":"05Pol",
                "Oec.":"06Oec",
                "Eth.":"07Eth",
                "Med.":"08Med",
                "Geogr.":"09Geog",
                "Astron.":"10Astr",
                "Phys.":"11Phys",
                "Geom.":"12Geom",
                "Arith.":"13Arit",
                "Poet.":"14Poet",
                "Log.":"15Log",
                "Rhet.":"16Rhet",
                "Gramm.":"17Gram",
                "Quod.":"18Quod"
            }
            if self.group in conc:
                return(conc[self.group]) 
            else:
                print("Fehler bei " + self.whole + "!")
                return(self.group)
        def makeSortableRoot(self):
            sortColl = self.collection.ljust(3, "0")
            sortFormat = "99"
            if self.format == "FM":
                sortFormat = "FM"
            elif self.format != "":
                sortFormat = self.format.replace("°", "").zfill(2)
            sortGroup = "000000"
            if self.group:
                sortGroup = self.translateGroup()
                sortGroup = sortGroup.strip(".").ljust(6, "0")
            sortForm = "0"
            if self.form != "":
                sortForm = self.form[0]
            res = [sortColl, sortGroup, sortFormat, sortForm, self.sortableNum(self.number), self.sortableNum(self.volume)]
            return(".".join(res))
        def makeSortablePart(self):
            num = "0000"
            let = "00"
            extract = re.search(r"([0-9]+)([a-z]+)?", self.part)
            try:
                num = extract.group(1)[0:3]
            except:
                pass
            try:
                let = extract.group(2)[0:1]
            except:
                pass
            return(num.zfill(4) + let.zfill(2))
        def makeSortable(self):
            return(f"{self.makeSortableRoot()}.{self.makeSortablePart()}")
class ShelfmarkList():
    def __init__(self, content = []):
        self.content = []   
        self.volumeDict = {}
        for sm in content:
            self.addSM(sm)
        self.volumeList = []
    def __iter__(self):
        self.a = 0
        return(self)
    def __next__(self):
        if self.a < len(self.volumeList):
            ret = self.volumeList[self.a]
            self.a += 1
            return(ret)
        else:
            raise StopIteration        
    def addSM(self, sm):
        if isinstance(sm, StructuredShelfmark):
            self.content.append(sm)
    def makeVolumes(self):
        for shm in self.content:
            if shm.part:
                try:
                    self.volumeDict[shm.bareRoot].parts.append(shm.part)
                except:
                    self.volumeDict[shm.bareRoot] = Volume(shm.bareRoot, shm.makeSortableRoot(), [shm.part])
            else:
                if shm.bareRoot in self.volumeDict.keys():
                    self.volumeDict[shm.bareRoot].parts.append("x")
                else:
                    self.volumeDict[shm.bareRoot] = Volume(shm.bareRoot, shm.makeSortableRoot())
        self.makeVolumeList()
    def makeVolumeList(self):
        self.volumeList = [self.volumeDict[vol] for vol in self.volumeDict]
        self.volumeList = sorted(self.volumeList, key=lambda v:v.sortable)
    def getByRoot(self, root):
        try:
            return(self.volumeDict[root])
        except:
            return(None)
class Volume():
    def __init__(self, bareRoot, sortable, parts = []):
        self.root = bareRoot
        self.sortable = sortable
        self.parts = []
        self.partStr = ""
        self.compStr = ""
        for part in parts:
            self.parts.append(part)
    def makePartStr(self):
        self.parts = sorted(self.parts, key=lambda p:StructuredShelfmark.makeSortablePart(None, p))
        self.partStr = ", ".join(self.parts)
        return(self.partStr)
    def makeCompStr(self):
        self.parts = sorted(self.parts, key=lambda p:StructuredShelfmark.makeSortablePart(None, p))
        if len(self.parts) < 3:
            self.compStr = ", ".join(self.parts)
            return(False)
        for part in self.parts:
            try:
                partInt = int(part)
            except:
                self.compStr = ", ".join(self.parts)
                return(False)
        length = len(self.parts)
        compParts = [self.parts[0]]
        i = 1
        while i < length - 1:
            if int(self.parts[i + 1]) == int(self.parts[i]) + 1 and int(self.parts[i - 1]) == int(self.parts[i]) - 1:
                if compParts[len(compParts) - 1] != "-":
                    compParts.append("-")
            else:
                compParts.append(self.parts[i])
            i += 1
        compParts.append(self.parts[length - 1])
        compStr = ", ".join(compParts)
        compStr = compStr.replace(", -, ", "-")
        self.compStr = compStr
        return(self.compStr)
    def __str__(self):
        ret = self.root
        if self.parts:
            self.makePartStr()
            self.makeCompStr()
            ret += " (" + self.compStr + ")"
        return(ret)

def convertVD16(old):
    if old[0:1] == "\"":
        old = old + ")"
    new = old.strip("\"")
    if new.find("Helmst") > 0 or new.find("QuH") == 0:
        new = "H: " + new
    elif re.search(r"Theol|Jur|Hist|Bell|Pol|Oec|Eth|Med|Geogr|Astr|Phys|Geom|Arit|Poet|Log|Rhet|Gram|Quod", new):
        new = "A: " + new
    elif re.match(r"[ABCDEFGHJKLMNOPQRSTUVZ][a-z]N? ", new):
        new = "M: " + new
    #elif new.find("Alv") == 0:
    #    new = "S. " + new
    new = new.replace("(", " (")
    new = new.replace("Alv ", "Alv.: ")
    new = new.replace("Lpr.Stolb.", "Lpr. Stolb. ")
    new = new.replace("Bibel-S.", "Bibel-S. ")
    new = new.replace("Helmst.Dr.", "Helmst. Dr.")
    new = new.replace("°H", "° H")
    try:
        letter = re.search(r"(\s)([a-z])", new).group(2)
    except:
        pass
    else:
        space = re.search(r"(\s)([a-z])", new).group(1)
        new = new.replace(space + letter, letter)
    try:
        num = re.search(r"([a-z]{2})\.([0-9])", new).group(2)
    except:
        pass
    else:
        letter = re.search(r"([a-z])\.([0-9])", new).group(1)
        new = new.replace(letter + "." +  num, letter + ". " +  num)
    try:
        numlet = re.search(r"([0-9][a-z]{1,2})\. ([0-9])", new).group(1)
    except:
        pass
    else:
        num = re.search(r"([0-9][a-z]{1,2})\. ([0-9])", new).group(2)
        new = new.replace(numlet + ". " + num, numlet + "." + num)    
    new = new.replace("  ", " ")
    new = new.replace("Li 5530 (", "Li 5530 Slg. Hardt (*, ")    
    new = insertPoint(new)
    new = adjustMus(new)
    return(new)
def adjustMus(sm):
    if "Mus" not in sm:
        return(sm)
    sm = sm.replace("Mus.", "Musica ")
    sm = sm.replace(" div", " div.")
    sm = sm.replace(" coll.inc.", " coll. inc.")
    sm = sm.replace(" Coll.Inc.", " coll. inc.")
    sm = sm.replace("fol.", " 2°")
    sm = sm.replace("H: ", "")
    sm = sm.replace("  ", " ")
    sm = sm.replace("..", ".")
    sm = sm.strip()
    return(sm)
def insertPoint(sm):
    stops = ["Schulenburg", "Kapsel"]
    for stop in stops:
        if stop in sm:
            return(sm)
    try:
        word = re.search(r"[A-Z][a-z]{2,}", sm).group(0)
    except:
        return(sm)
    else:
        sm = sm.replace(word, word + ".")
        sm = sm.replace("..", ".")
        return(sm)
def searchable(sm):
    sm = sm.replace("(", "\(")
    sm = sm.replace(")", "\)")
    return(sm)
    