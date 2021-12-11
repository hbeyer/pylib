#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import pica
from lib import sru
from lib import xmlreader as xr
from lib import dataset as ds
from ext import dspace_rest_client as drc
import xml.etree.ElementTree as et
import urllib.request as ur
import re
import os
import json
import shutil
import glob
import logging

class Harvester():
    def __init__(self, ppn_o, folder = "downloads", diglib = "inkunabeln"):
        self.valid = False
        self.ppn_o = ppn_o
        if not re.match("^[\d]{9,10}$", self.ppn_o):
            raise Exception(f"Ungültige PPN: {self.ppn_o}")
        self.folder = folder
        self.diglib = diglib
        self.image_list = []        
        file = ur.urlopen(f"http://unapi.k10plus.de/?id=gvk:ppn:{self.ppn_o}&format=picaxml")
        tree = et.parse(file)
        node = tree.getroot()        
        self.rec_o = pica.Record(node)       
        self.sig = self.rec_o.copies[0].sm
        self.digi = self.rec_o.digi
        search = re.search("http://diglib.hab.de/([^/]+)/([^/]+)/start.htm", self.digi)
        try:
            self.diglib = search.group(1)
        except:
            raise Exception("Die normalisierte Signatur konnte nicht gefunden werden")
        self.norm_sig = search.group(2)
        self.url_struct = f"http://diglib.hab.de/{self.diglib}/{self.norm_sig}/facsimile.xml"
        status_code = ur.urlopen(self.url_struct).getcode()
        if status_code != 200:
            raise Exception(f"Keine facsimile.xml unter {self.url_struct}")
        self.folder_ma = self.get_folder_ma()
        if self.folder_ma is None:
            raise Exception("Der Ordner auf dem MA-Server konnte nicht gefunden werden")
        self.path = f"{self.folder}/{self.norm_sig}"
        self.rec_a = None
        sig_sru = self.sig.replace("(", "").replace(")", "").replace(" ", "+")
        req = sru.Request_HAB()
        req.prepare("pica.sgb=" + sig_sru)
        wr = xr.webReader(req.url, tag = "record", namespace = "http://docs.oasis-open.org/ns/search-ws/sruResponse")
        for node in wr:
            rc = pica.RecordInc(node)
            if rc.bbg[0] == "A":
                self.rec_a = rc
                self.ppn_a = self.rec_a.ppn
        if self.rec_a == None:
            logging.warning(f"Keine A-Aufnahme über SRU gefunden")
            self.rec_a = self.rec_o
        self.extract_metadata()
        try:
            self.meta_list = self.meta.to_list()
        except:
            raise Exception("Die Metadaten konnten nicht geladen werden")
        self.valid = True
    def __str__(self):
        ret = f"Harvester für {self.digi} \n \
        PPN: {self.ppn_o} (Digitalisat), {self.ppn_a} (Vorlage) \n \
        Normalisierte Signatur: {self.norm_sig} \n \
        Pfad Master-Images: {self.folder_ma} \n \
        Valide: {'ja' if self.valid == True else 'nein'}" 
        return(ret)
    def to_folder(self, overwrite_images = False):
        logging.info(f"Harvesten des Digitalisats mit der PPN {self.ppn_o}")
        self.make_folder()
        self.download_xml()
        self.download_images(overwrite_images = overwrite_images)
        self.save_metadata()
        logging.info(f"Dateien geladen im Ordner {self.path}")
    def make_folder(self):
        if os.path.exists(self.path):
            pass
        else:
            os.mkdir(self.path)
    def download_xml(self):
        url_o = f"http://unapi.k10plus.de/?id=gvk:ppn:{self.ppn_o}&format=picaxml"
        try:
            ur.urlretrieve(url_o, self.path + "/o-aufnahme.xml")
        except:
            logging.warning("Laden der O-Aufnahme fehlgeschlagen")
        try:
            ur.urlretrieve(f"http://unapi.k10plus.de/?id=gvk:ppn:{self.ppn_a}&format=picaxml", f"{self.path}/a-aufnahme.xml")
        except:
            logging.info("Laden der A-Aufnahme fehlgeschlagen")        
        url_mets = f"http://oai.hab.de/?verb=GetRecord&metadataPrefix=mets&identifier=oai:diglib.hab.de:ppn_{self.ppn_o}"
        try:
            ur.urlretrieve(url_mets, self.path + "/mets.xml")
        except:
            logging.info("Laden der METS fehlgeschlagen")
        try:
            ur.urlretrieve(self.url_struct, self.path + "/facsimile.xml")
        except:
            logging.warning("Laden der facsimile.xml fehlgeschlagen")
        url_transcr = f"http://diglib.hab.de/{self.diglib}/{self.norm_sig}/tei-struct.xml"
        try:
            ur.urlretrieve(url_transcr, self.path + "/tei-struct.xml")
        except:
            logging.info("Keine tei-struct.xml gefunden")
    def download_images(self, overwrite_images):
        with open(self.path + "/facsimile.xml", "r") as file:
            tree = et.parse(file)
            root = tree.getroot()
            for gr in root:
                im_name = gr.attrib["url"].split("/").pop()
                self.image_list.append(im_name)
            for im in self.image_list:
                original = self.folder_ma + im.replace("jpg", "tif")
                target = self.path + "/" + im.replace("jpg", "tif")
                if os.path.exists(target) == False or overwrite_images == True:
                        shutil.copyfile(original, target)
    def extract_metadata(self):
        self.meta = ds.DatasetDC()
        self.meta.add_entry("dc.identifier", ds.Entry(self.rec_o.digi))
        self.meta.add_entry("dc.format", ds.Entry("Online resource", "eng"))
        self.meta.add_entry("dc.type", ds.Entry("Digitized book", "eng"))
        self.meta.add_entry("dc.title", ds.Entry(self.rec_a.title))
        self.meta.add_entry("dc.date", ds.Entry(self.rec_a.date))
        for pers in self.rec_a.persons:
            pers.makePersName()
            if pers.role == "dc.creator":
                self.meta.add_entry("dc.creator", ds.Entry(pers.persName, None, "GND", pers.gnd))
            else:
                self.meta.add_entry("dc.contributor", ds.Entry(pers.persName, None, "GND", pers.gnd))
        for pub in self.rec_a.publishers:
            pub.makePersName()
            self.meta.add_entry("dc.publisher", ds.Entry(pub.persName, None, "GND", pub.gnd))
        for lng in self.rec_a.lang:
            self.meta.add_entry("dc.language", ds.Entry(lng))
        for sub in self.rec_a.subjects:
            self.meta.add_entry("dc.subject", ds.Entry(sub))
        mat_type = self.get_mat_type()
        self.meta.add_entry("dc.description", ds.Entry(mat_type + " aus dem Bestand der Herzog August Bibliothek Wolfenbüttel", "ger"))
        self.meta.add_entry("dc.rights", ds.Entry("CC BY-SA 3.0"))
        self.meta.add_entry("dc.rights.uri", ds.Entry("http://diglib.hab.de/copyright.html"))
        self.meta.add_entry("dcterms.rightsHolder", ds.Entry("Herzog August Bibliothek Wolfenbüttel"))
        self.meta.add_entry("dc.source", ds.Entry(f"Wolfenbüttel, Herzog August Bibliothek, {self.sig}"))
        try:
            self.meta.add_entry("dc.relation", ds.Entry(self.rec_a.gw))
        except:
            pass
        try:
            self.meta.add_entry("dc.relation", ds.Entry(self.rec_a.istc))
        except:
            pass
    def save_metadata(self):
        meta = self.meta.to_list()
        with open(self.path + "/metadata.json", "w") as target:
            json.dump(meta, target, indent=2, ensure_ascii=False)
    def get_mat_type(self):
        if self.diglib == "inkunabeln" or re.match("14\d\d|1500", self.rec_a.date):
            return("Digitalisierte Inkunabel")
        return("Digitalisierter Druck")
    def get_folder_ma(self):
        if self.diglib == "inkunabeln":
            return(f"//MASERVER/Auftraege/Master/{self.diglib}/{self.norm_sig}/")
        if self.diglib == "drucke":
            proceed = True
            druck_no = 1
            while proceed == True:
                path = f"//MASERVER/Auftraege/Master/drucke{str(druck_no).zfill(2)}/drucke/{self.norm_sig}/"
                if os.path.exists(path):
                    return(path)
                druck_no += 1
                if druck_no > 15:
                    proceed = False
        return(None)

def Uploader():
    def __init__(self, user, password, rest_url, collection):
        self.valid = False
        self.client = drc.DSpaceRestClient(user, password, rest_url, False, True)
        if self.client is None:
            raise Exception(f"Fehler beim Erzeugen des REST-Clients für {rest_url}, user {user}")
        self.collection_id = self.client.get_id_by_handle(collection)
        if collection_id is None:
            raise Exception(f"ID für die Collection {collection} konnte nicht gefunden werden")
        else:
            self.valid = True