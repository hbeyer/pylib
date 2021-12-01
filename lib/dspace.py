#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import pica
from lib import sru
from lib import xmlreader as xr
from lib import dataset as ds
import xml.etree.ElementTree as et
import urllib.request as ur
import re
import os
import json
import shutil
import glob
import logging

class Harvester():
    def __init__(self, ppnO, folder = "downloads", diglib = "inkunabeln"):
        self.ppnO = ppnO
        self.folder = folder
        self.diglib = diglib
        file = ur.urlopen(f"http://unapi.k10plus.de/?id=gvk:ppn:{self.ppnO}&format=picaxml")
        tree = et.parse(file)
        node = tree.getroot()        
        self.recO = pica.Record(node)
        self.sig = self.recO.copies[0].sm
        search = re.search("http://diglib.hab.de/([^/]+)/([^/]+)/start.htm", self.recO.digi)
        try:
            self.diglib = search.group(1)
        except:
            logging.warning("Die normalisierte Signatur konnte nicht gefunden werden")
        self.normSig = search.group(2)
        self.folderMA = self.getFolderMA()
        self.path = f"{self.folder}/{self.normSig}"
        self.recA = None
        sigSRU = self.sig.replace("(", "").replace(")", "").replace(" ", "+")
        req = sru.Request_HAB()
        req.prepare("pica.sgb=" + sigSRU)
        wr = xr.webReader(req.url, tag = "record", namespace = "http://docs.oasis-open.org/ns/search-ws/sruResponse")
        for node in wr:
            rc = pica.RecordInc(node)
            if rc.bbg[0] == "A":
                self.recA = rc
                self.ppnA = self.recA.ppn
        if self.recA == None:
            self.recA = self.recO
        self.imageList = []
    def go(self, overwriteImages = False):
        logging.info(f"Harvesten des Digitalisats mit der PPN {self.ppnO}")
        self.makeFolder()
        self.downloadXML()
        self.downloadImages(overwriteImages = overwriteImages)
        self.extractMetadata()
        self.saveMetadata()
        logging.info(f"Dateien geladen im Ordner {self.path}")
    def makeFolder(self):
        if os.path.exists(self.path):
            pass
        else:
            os.mkdir(self.path)
    def downloadXML(self):
        urlO = f"http://unapi.k10plus.de/?id=gvk:ppn:{self.ppnO}&format=picaxml"
        try:
            ur.urlretrieve(urlO, self.path + "/o-aufnahme.xml")
        except:
            logging.warning("Laden der O-Aufnahme fehlgeschlagen")
        try:
            ur.urlretrieve(f"http://unapi.k10plus.de/?id=gvk:ppn:{self.ppnA}&format=picaxml", f"{self.path}/a-aufnahme.xml")
        except:
            logging.info("Laden der A-Aufnahme fehlgeschlagen")        
        urlMets = f"http://oai.hab.de/?verb=GetRecord&metadataPrefix=mets&identifier=oai:diglib.hab.de:ppn_{self.ppnO}"
        try:
            ur.urlretrieve(urlMets, self.path + "/mets.xml")
        except:
            logging.info("Laden der METS fehlgeschlagen")
        urlStruct = f"http://diglib.hab.de/{self.diglib}/{self.normSig}/facsimile.xml"
        try:
            ur.urlretrieve(urlStruct, self.path + "/facsimile.xml")
        except:
            logging.warning("Laden der facsimile.xml fehlgeschlagen")
        urlTranscr = f"http://diglib.hab.de/{self.diglib}/{self.normSig}/tei-struct.xml"
        try:
            ur.urlretrieve(urlTranscr, self.path + "/tei-struct.xml")
        except:
            logging.info("Keine tei-struct.xml gefunden")
    def downloadImages(self, overwriteImages):
        with open(self.path + "/facsimile.xml", "r") as file:
            tree = et.parse(file)
            root = tree.getroot()
            for gr in root:
                imName = gr.attrib["url"].split("/").pop()
                self.imageList.append(imName)
            for im in self.imageList:
                original = self.folderMA + im.replace("jpg", "tif")
                target = self.path + "/" + im.replace("jpg", "tif")
                if os.path.exists(target) == False or overwriteImages == True:
                        shutil.copyfile(original, target)
    def extractMetadata(self):
        self.meta = ds.DatasetDC()
        self.meta.addEntry("identifier", ds.Entry(self.recO.digi))
        self.meta.addEntry("format", ds.Entry("Online resource", "eng"))
        self.meta.addEntry("type", ds.Entry("Digitized book", "eng"))
        self.meta.addEntry("title", ds.Entry(self.recA.title))
        self.meta.addEntry("date", ds.Entry(self.recA.date))
        for pers in self.recA.persons:
            pers.makePersName()
            if pers.role == "creator":
                self.meta.addEntry("creator", ds.Entry(pers.persName, None, "GND", pers.gnd))
            else:
                self.meta.addEntry("contributor", ds.Entry(pers.persName, None, "GND", pers.gnd))
        for pub in self.recA.publishers:
            pub.makePersName()
            self.meta.addEntry("publisher", ds.Entry(pub.persName, None, "GND", pub.gnd))
        for lng in self.recA.lang:
            self.meta.addEntry("language", ds.Entry(lng))
        for sub in self.recA.subjects:
            self.meta.addEntry("subject", ds.Entry(sub))
        matType = self.getMatType()
        self.meta.addEntry("description", ds.Entry(matType + " aus dem Bestand der Herzog August Bibliothek Wolfenbüttel", "ger"))
        self.meta.addEntry("rights", ds.Entry("CC BY-SA 3.0"))
        self.meta.addEntry("rights", ds.Entry("http://diglib.hab.de/copyright.html"))
        self.meta.addEntry("source", ds.Entry(f"Wolfenbüttel, Herzog August Bibliothek, {self.sig}"))
        try:
            self.meta.addEntry("relation", ds.Entry(self.recA.gw))
        except:
            pass
        try:
            self.meta.addEntry("relation", ds.Entry(self.recA.istc))
        except:
            pass
    def saveMetadata(self):
        meta = self.meta.toList()
        with open(self.path + "/metadata.json", "w") as target:
            json.dump(meta, target, indent=2, ensure_ascii=False)
    def getMatType(self):
        if self.diglib == "inkunabeln" or re.match("14\d\d|1500", self.recA.date):
            return("Digitalisierte Inkunabel")
        return("Digitalisierter Druck")
    def getFolderMA(self):
        if self.diglib == "inkunabeln":
            return(f"//MASERVER/Auftraege/Master/{self.diglib}/{self.normSig}/")
        if self.diglib == "drucke":
            proceed = True
            druckNo = 1
            while proceed == True:
                path = f"//MASERVER/Auftraege/Master/drucke{str(druckNo).zfill(2)}/drucke/{self.normSig}/"
                if os.path.exists(path):
                    return(path)
                druckNo += 1
                if druckNo > 15:
                    proceed = False
        return(None)
