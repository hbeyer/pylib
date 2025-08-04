#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import httpx
import re
import os
import xml.etree.ElementTree as et
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib.namespace import FOAF, RDF, DC, DCTERMS, OWL, RDF, RDFS, SKOS, XSD
from lib import sru
from lib import xmlreader as xr
from lib import image_resolver as ir
from lib import pica
from lib import cache
from lib import iiif
# https://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf.html
logging.basicConfig(level=logging.INFO)

class Book:
    def __init__(self, norm_sig, folder = None):
        self.folder = "drucke"
        if folder != None:
            self.folder = folder
        self.norm_sig = norm_sig
        self.year_digi = None
        self.bib_record = None
        self.pages = []
        self.struct_doc = None
        self.ranges = []
        self.export_folder = "manifests"
        self.graph = None
        self.namespaces = {}
        self.cache_sru = cache.CacheSRU_O()
        self.cache_facs = cache.CacheFacsimile()
        self.cache_struct = cache.CacheStruct()
        self.cache_dim = cache.CacheImageDimensions()
        self.resolver = ir.Resolver()
        self.get_year_digi()
        self.get_bib_data()
        self.get_pages()
        self.get_struct_doc()
        if self.struct_doc != None:
            self.get_ranges()
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
        url = f"http://sru.k10plus.de/opac-de-23?version=2.0&operation=searchRetrieve&query=pica.url=diglib.hab.de{self.folder}{self.norm_sig}start.htm and pica.bbg=o*&maximumRecords=1&startRecord=1&recordSchema=picaxml"
        xml = self.cache_sru.get_xml(url, f"{self.folder}_{self.norm_sig}")
        reader = xr.StringReader(xml, "record", "http://docs.oasis-open.org/ns/search-ws/sruResponse")
        for node in reader:
            self.bib_record = pica.Record(node)
            return(True)
        return(False)
    def get_pages(self):
        xml = self.cache_facs.get_xml(self.norm_sig, self.folder)
        if xml == None:
            loggin.error(f" Seiten zu {self_folder}/{self.norm_sig} konnten nicht geladen werden")
            return
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
            self.pages.append((image_no, number, ""))
    def get_struct_doc(self):
        xml = self.cache_struct.get_xml(self.norm_sig, self.folder)
        if xml == None:
            logging.info(f" Keine Strukturdaten zu {self.folder}/{self.norm_sig}")
            return
        self.struct_doc = et.fromstring(xml)
        return
    def get_ranges(self):
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
        return
    def to_iiif(self, folder = None):
        if folder != None:
            self.export_folder = folder
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
        self.get_year_digi()
        main_res = f"https://diglib.hab.de/{self.folder}/{self.norm_sig}/manifest.json"
        manifest = iiif.Manifest(main_res)
        if self.bib_record:
            label = self.bib_record.make_citation()
            manifest.add_label(label)
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
            manifest.add_homepage("Katalogeintrag", "Catalogue entry", f"https://opac.lbs-braunschweig.gbv.de/DB=2/XMLPRS=N/PPN?PPN={self.bib_record.ppn}")
        for page in self.pages:
            image_no, number, _struct = page
            base_do = f"https://diglib.hab.de/{self.folder}/{self.norm_sig}"
            base_api = f"https://image.hab.de/iiif/images/{self.folder}/{self.norm_sig}/{self.year_digi}_standard_original/{self.norm_sig}_{image_no}.jp2/"
            url_info = self.resolver.make_link(self.norm_sig, self.year_digi, self.folder, image_no)
            dimensions = self.cache_dim.get(url_info)
            if dimensions == None:
                logging.error(f" Abmessungen konnten nicht geladen werden für {self.norm_sig} Image {image_no}")
                continue
            width, height = dimensions.split(",")
            manifest.add_page_lazily(base_do, base_api, image_no, height, width, 'image/jpeg')
        if len(self.ranges) > 0:
            manifest.add_structures(base_do, self.ranges)
        return(manifest)
        
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