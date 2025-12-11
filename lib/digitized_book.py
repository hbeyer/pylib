#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import httpx
import re
import os
import xml.etree.ElementTree as et
from lib import sru
from lib import unapi as ua
from lib import xmlreader as xr
from lib import image_resolver as ir
from lib import pica
from lib import cache
from lib import iiif
# https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf.html

class Book:
    def __init__(self, norm_sig, folder = None):
        self.folder = "drucke"
        self.rights = "https://creativecommons.org/publicdomain/mark/1.0/"
        if folder != None:
            self.folder = folder
        self.norm_sig = norm_sig
        self.year_digi = None
        self.bib_record = None
        self.pages = []
        self.images = []
        self.struct_doc = None
        self.ranges = []
        self.cache_sru = cache.CacheSRU_O()
        self.cache_facs = cache.CacheFacsimile()
        self.cache_struct = cache.CacheStruct()
        self.cache_dim = cache.CacheImageDimensions()
        self.resolver = ir.Resolver()
        self.client = httpx.Client(default_encoding="utf-8")
    def get_legacy_data(self):
        self.get_year_digi()
        self.get_bib_data()
        self.get_pages()
        self.get_struct_doc()
        if self.struct_doc != None:
            self.get_ranges()
    def read_log(self):
        url_tiff = f"https://image.hab.de/images/{self.folder}/{self.norm_sig}/{self.folder}-convert-tiff-jp2.log"
        url_jpg = f"https://image.hab.de/images/{self.folder}/{self.norm_sig}/{self.folder}-cp-jpg.log"
        req = self.client.get(url_tiff)
        if req.status_code != 200:
            req = self.client.get(url_jpg)
            if req.status_code != 200:
                return(False)
        lines = req.text.split("\n")
        for line in lines:
            if line.strip() == "":
                continue
            #extr = re.search(r"\d+.(jpg|tiff) (/images/([^/]+)/([^/]+)/(12]\d{3})_standard_original/([^ ]+)) (\d+)x(\d+)", line)
            extr = re.search(r"/([^/]+)\.(jpg|tif) (/images/([^/]+)/([^/]+)/([12]\d{3})_standard_original/([^ ]+)) (\d+)x(\d+)", line)
            try:
                self.year_digi = extr.group(5)
            except:
                logging.error(f"Kein Digitalisierungsjahr im Logfile, Signatur {self.norm_sig}")
            else:
                year_digi = self.year_digi
            try:
                image_number = extr.group(1)
            except:
                logging.error(f"Fehlende Image-Nummer im Logfile, Signatur {self.norm_sig}")
                continue
            try:
                image_path = extr.group(3)
            except:
                logging.error(f"Fehlender Image-Path im Logfile, Signatur {self.norm_sig}")
                continue                
            try:
                width = extr.group(8)
                height = extr.group(9)                
            except:
                logging.error(f"Nicht lesbare Abmessungen im Log für Signatur {self.norm_sig}") 
                continue
            self.images.append(Image(image_number, image_path, height, width))
        return(True)
    def get_page_labels_diglib(self):
        if len(self.pages) == 0:
            self.get_pages()
        page_dict = { tup[0] : tup[1] for tup in self.pages }
        for image in self.images:
            try:
                image.label = page_dict[image.number]
            except:
                pass
    def get_year_digi(self):
        self.year_digi = self.resolver.get_digi_year(self.norm_sig, self.folder)
        if self.year_digi == None:
            # Zusatzprüfung für den Fall, dass das Digitalisat seit der letzten Prüfung abrufbar gemacht wurde
            self.resolver.forget_item(self.norm_sig, self.folder);
            self.year_digi = self.resolver.get_digi_year(self.norm_sig, self.folder)
            if self.year_digi == None:
                logging.error(f" Es konnte kein Digitalisierungsjahr zu {self.folder}/{self.norm_sig} gefunden werden")
                return(False)
        return(True)
    def get_bib_data(self):
        url = f"http://sru.k10plus.de/opac-de-23?version=2.0&operation=searchRetrieve&query=pica.url=diglib.hab.de{self.folder}{self.norm_sig}*+and+pica.bbg=o*&maximumRecords=1&startRecord=1&recordSchema=picaxml"
        resp = self.client.get(url)
        if resp.status_code != 200:
            logging.error(f" Keine O-Aufnahme zu {norm_sig} gefunden")
            return(False)
        #xml = self.cache_sru.get_xml(url, f"{self.folder}_{self.norm_sig}")
        xml = resp.text
        reader = xr.StringReader(xml, "record", "http://docs.oasis-open.org/ns/search-ws/sruResponse")
        for node in reader:
            self.bib_record = pica.RecordO(node)
            return(True)
        return(False)
    def get_pages(self):
        xml = self.cache_facs.get_xml(self.norm_sig, self.folder)
        if xml == None:
            loggin.error(f" Seiten zu {self_folder}/{self.norm_sig} konnten nicht geladen werden")
            return(False)
        reader = xr.StringReader(xml, tag = "graphic", namespace = "http://www.tei-c.org/ns/1.0")
        for node in reader:
            image = node.attrib.get("url", "")
            extr = re.search("(eb\d{2}|\d{5}[a-z]?)\.jpg", image)            
            try:
                image_no = extr.group(1)
            except:
                image_no = ""
                logging.error(f" Problem bei Image {image}")
            number = node.attrib.get("n", "")
            self.pages.append((image_no, number))
        return(True)
    def get_struct_data(self):
        self.get_struct_doc()
        if self.struct_doc == None:
            return(False)
        divs = self.struct_doc.findall(".//{http://www.tei-c.org/ns/1.0}div")
        for div in divs:
            div_type = div.attrib.get("type", "")
            head = div.find(".//{http://www.tei-c.org/ns/1.0}head")
            try:
                heading = head.text
            except:
                heading = None
            range = Range(heading, div_type)
            pbs = div.findall(".//{http://www.tei-c.org/ns/1.0}pb")
            for pb in pbs:
                facs = pb.attrib.get("facs", "")
                image_no = facs.replace(f"#{self.folder}_{self.norm_sig}_", "")
                num = pb.attrib.get("n", "")
                range.add_page((image_no, num))
            self.ranges.append(range)
            indices = div.findall(".//{http://www.tei-c.org/ns/1.0}index")
            for ind in indices:
                facs = ind.attrib.get("facs", "")
                image_no = facs.replace(f"#{self.folder}_{self.norm_sig}_", "")
                term = ind.find(".//{http://www.tei-c.org/ns/1.0}term")
                try:
                    term_label = term.text
                    term_type = term.attrib.get("type", "structure")
                except:
                    continue
                else:
                    range = Range(term_label, term_type)
                    range.add_page((image_no, ""))
                    self.ranges.append(range)
        return(True)
    def get_struct_doc(self):
        xml = self.cache_struct.get_xml(self.norm_sig, self.folder)
        if xml == None:
            logging.info(f" Keine Strukturdaten zu {self.folder}/{self.norm_sig}")
            return(False)
        self.struct_doc = et.fromstring(xml)
        return(True)
    def to_iiif(self):
        if self.bib_record == None:
            self.get_bib_data()
        if len(self.images) == 0:
            self.read_log()
        if len(self.pages) == 0:
            self.get_pages()
        self.get_page_labels_diglib()
        if len(self.ranges) == 0:
            self.get_struct_data()
        main_res = f"https://diglib.hab.de/{self.folder}/{self.norm_sig}/manifest.json"
        manifest = iiif.Manifest(main_res)
        if self.bib_record:
            label = self.bib_record.make_citation()
            manifest.add_label(label, "de")
            manifest.add_label(label, "en")
            for pers in self.bib_record.persons:
                if pers.role in ["VerfasserIn", "Verfasser", "creator"]:
                    manifest.add_metadata_property("VerfasserIn", pers.persName, "Author")
            manifest.add_metadata_property("Titel", self.bib_record.title, "Title")
            if self.bib_record.edition:
                manifest.add_metadata_property("Ausgabe", self.bib_record.edition, "Edition")
            if len(self.bib_record.publishers) > 0:
                pub_str = "; ".join([pub.persName for pub in self.bib_record.publishers])
                manifest.add_metadata_property("Drucker/Verlag", pub_str, "Publisher")
            if len(self.bib_record.places) > 0:
                place_str = "; ".join([pl.placeName for pl in self.bib_record.places])
                manifest.add_metadata_property("Erscheinungsort", place_str, "Place")                
            manifest.add_metadata_property("Datum", self.bib_record.date, "Date")
            phys_descr = self.bib_record.pages
            if self.bib_record.format:
                phys_descr = phys_descr + ", " + self.bib_record.format
            if self.bib_record.illustrations:
                phys_descr = phys_descr + ", " + self.bib_record.illustrations
            manifest.add_metadata_property("Physische Beschreibung", phys_descr, "Physical description")
            if self.bib_record.vdn:
                manifest.add_metadata_property("VD-Nr.", self.bib_record.vdn, "No. VD")
            manifest.add_metadata_property("Besitzende Institution", self.bib_record.institution_original, "Physical location")
            manifest.add_metadata_property("Ländercode", self.bib_record.country_original, "Country")
            manifest.add_metadata_property("Signatur", self.bib_record.shelfmark_original, "Shelfmark")
            manifest.add_metadata_property("Lizenz", self.rights, "Copyright")
            manifest.add_homepage("Katalogeintrag", "Catalogue entry", f"https://opac.lbs-braunschweig.gbv.de/DB=2/XMLPRS=N/PPN?PPN={self.bib_record.ppn}")
        base_do = f"https://diglib.hab.de/{self.folder}/{self.norm_sig}"
        for im in self.images:
            base_api = f"https://image.hab.de/iiif{im.path}/"
            manifest.add_page_lazily(base_do, base_api, im.number, im.height, im.width, 'image/jpeg', im.label)
        if len(self.ranges) > 0:
            manifest.add_structures(base_do, self.ranges)            
        return(manifest)

class Image:
    def __init__(self, number, path = None, height = None, width = None, label = None):
        self.number = number
        self.path = ""
        self.label = ""
        if label != None:
            self.label = label
        if path != None:
            self.path = path
        self.height = height
        self.width = width
    def __str__(self):
        page_number = ""
        if self.label != "":
            page_number = f"S. {self.label}, "
        im_str = f"Image Nr. {self.number}, {page_number}{self.height}x{self.width}, Pfad: {self.path}"
        return(im_str)

class Range:
    def __init__(self, heading = None, type = None):
        self.heading = ""
        if heading != None:
            self.heading = heading
        self.type = ""
        if type != None:
            self.type = type
        self.pages = []
    def add_page(self, tuple):
        if len(tuple) != 2:
            return(False)
        self.pages.append(tuple)
        return(True)
    def __str__(self):
        if self.heading == "":
            self.heading = "ohne Titel"
        if self.type == "":
            self.type = "unbestimmt"
        ret = f"Abschnitt {self.heading}, Typ {self.type}, {len(self.pages)} Seiten"
        return(ret)
        
def get_norm_sig(ppn):
    if re.match(f"^[\dX]{8,11}$", ppn) == False:
        return(None)
    req = ua.Request_unAPI()
    req.prepare(ppn)
    url = req.url
    reader = xr.WebReader(url, "record", "info:srw/schema/5/picaXML-v1.0")
    for node in reader:
        rec = pica.Record(node)
        if len(rec.digi) == 0:
            logging.error(f"Keine URL in O-Aufnahme {ppn} gefunden")
        for url_digi in rec.digi:
            extr = re.search(r"(drucke|inkunabeln|edoc|varia/selecta)/[^/]+", url_digi)
            if extr != None:
                return(extr.group(0))
    return(None)