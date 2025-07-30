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
        return(manifest)
        
    def _to_iiif(self, folder = None):
        if folder != None:
            self.export_folder = folder
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
        self.create_graph()
        man_res = URIRef(f"https://diglib.hab.de/{self.folder}/{self.norm_sig}/manifest.json")        
        self.graph.add((man_res, RDF.type, self.namespaces["SC"].Manifest))
        #self.graph.add((man_res, RDF.context, URIRef("http://iiif.io/api/presentation/3/context.json")))
        context = "http://iiif.io/api/presentation/3/context.json"
        self.graph.add((man_res, FOAF.logo, URIRef("https://dev.hab.de/signaturen/public/assets/icons/logo.svg")))
        
        if self.bib_record:
            label = self.bib_record.make_citation()
            self.graph.add((man_res, RDFS.label, Literal(label)))
            for pers in self.bib_record.persons:
                if pers.role in ["VerfasserIn", "Verfasser", "creator"]:
                    pers_node = BNode()
                    self.graph.add((pers_node, RDFS.label, Literal("AutorInnen", lang="ger")))
                    self.graph.add((pers_node, RDF.value, Literal(pers.persName)))
                    self.graph.add((man_res, self.namespaces["SC"].metadataLabels, pers_node))

            tit_node = BNode()
            self.graph.add((tit_node, RDFS.label, Literal("Titel", lang="ger")))
            self.graph.add((tit_node, RDFS.label, Literal(self.bib_record.title)))
            self.graph.add((man_res, self.namespaces["SC"].metadataLabels, tit_node))

            date_node = BNode()
            self.graph.add((date_node, RDFS.label, Literal("Datierung", lang="ger")))
            self.graph.add((date_node, RDFS.label, Literal(self.bib_record.date)))
            self.graph.add((man_res, self.namespaces["SC"].metadataLabels, date_node))

            if len(self.bib_record.publishers) > 0:
                pub_node = BNode()
                self.graph.add((pub_node, RDFS.label, Literal("Drucker/Verleger", lang="ger")))
                self.graph.add((pub_node, RDFS.label, Literal("; ".join([pub.persName for pub in self.bib_record.publishers]))))
                self.graph.add((man_res, self.namespaces["SC"].metadataLabels, pub_node))

            if len(self.bib_record.places) > 0:
                place_node = BNode()
                self.graph.add((place_node, RDFS.label, Literal("Erscheinungsort", lang="ger")))
                self.graph.add((place_node, RDFS.label, Literal("; ".join([pl.placeName for pl in self.bib_record.places]))))  
                self.graph.add((man_res, self.namespaces["SC"].metadataLabels, place_node))                

            pages_node = BNode()
            self.graph.add((pages_node, RDFS.label, Literal("Umfang", lang="ger")))
            self.graph.add((pages_node, RDFS.label, Literal(self.bib_record.pages)))
            self.graph.add((pages_node, RDFS.label, Literal(self.bib_record.format)))
            if self.bib_record.illustrations:
                self.graph.add((pages_node, RDFS.label, Literal(self.bib_record.illustrations)))
            self.graph.add((man_res, self.namespaces["SC"].metadataLabels, pages_node))
            
            if self.bib_record.vdn:
                vd_node = BNode()
                self.graph.add((vd_node, RDFS.label, Literal("VD-Nummer", lang="ger")))
                self.graph.add((vd_node, RDFS.label, Literal(self.bib_record.vdn)))  
                self.graph.add((man_res, self.namespaces["SC"].metadataLabels, vd_node))
            
        main_seq = URIRef(f"https://diglib.hab.de/{self.folder}/{self.norm_sig}/start.htm#sequence-1")
        self.graph.add((main_seq, RDF.type, self.namespaces["SC"].Sequence))
        self.graph.add((main_seq, RDFS.label, Literal("Current order", lang="eng")))
        self.graph.add((man_res, self.namespaces["SC"].hasSequences, main_seq))
        
        for page in self.pages:
            image = page[0]
            num = page[1]
            label = num if num else f"[{image}]"
            url_info = self.resolver.make_link(self.norm_sig, self.year_digi, self.folder, image)
            dimensions = self.cache_dim.get(url_info)
            if dimensions == None:
                logging.error(f" Keine Abmessungen zu {self.folder}/{self.norm_sig} gefunden")
                continue
            canv_node = URIRef(f"https://diglib.hab.de/{self.folder}/{self.norm_sig}/start.htm#canvas-{image}")
            self.graph.add((canv_node, RDF.type, self.namespaces["SC"].Canvas))
            self.graph.add((canv_node, RDFS.label, Literal(label)))
            width, height = dimensions.split(",")
            self.graph.add((canv_node, self.namespaces["EXIF"].height, Literal(int(height), datatype=XSD.integer)))
            self.graph.add((canv_node, self.namespaces["EXIF"].width, Literal(int(width), datatype=XSD.integer)))
            self.graph.add((man_res, self.namespaces["SC"].hasCanvases, canv_node))
            
            ann_node = URIRef(f"https://diglib.hab.de/{self.folder}/{self.norm_sig}/start.htm#annotation-{image}")
            self.graph.add((canv_node, self.namespaces["SC"].hasAnnotations, ann_node))
            self.graph.add((ann_node, RDF.type, self.namespaces["OA"].Annotation))
            self.graph.add((ann_node, self.namespaces["OA"].motivatedBy, self.namespaces["SC"].painting))

            im_node = URIRef(self.resolver.make_default(self.norm_sig, self.year_digi, self.folder, image))
            self.graph.add((im_node, RDF.type, self.namespaces["DCTYPES"].Image))
            self.graph.add((im_node, self.namespaces["SVCS"].hasService, URIRef(url_info)))
            self.graph.add((im_node, self.namespaces["EXIF"].height, Literal(int(height), datatype=XSD.integer)))
            self.graph.add((im_node, self.namespaces["EXIF"].width, Literal(int(width), datatype=XSD.integer)))
            self.graph.add((im_node, DC.format, Literal("image/jpeg")))
            self.graph.add((ann_node, self.namespaces["OA"].hasBody, im_node))
            self.graph.add((ann_node, self.namespaces["OA"].hasTarget, canv_node))
            
        self.save_to_location("C:/Users/beyer/Documents/08 Querschnittsaufgaben/WDB/IIIF/Drucke/test_man_generator.json", "json-ld", context, True)
        self.save_to_location("C:/Users/beyer/Documents/08 Querschnittsaufgaben/WDB/IIIF/Drucke/test_man_generator.xml", "xml", None, False)
        self.save_to_location("C:/Users/beyer/Documents/08 Querschnittsaufgaben/WDB/IIIF/Drucke/test_man_generator.ttl", "turtle", None, False)
        #print(self.graph.serialize(format="json-ld", auto_compact=True))
        #print(self.graph.serialize(format="json-ld", context=context))

    def save_to_location(self, path, format, context = None, auto_compact=None):
        with open(path, "w", encoding="utf-8") as f:
            content = self.graph.serialize(format=format, context=context, auto_compact=auto_compact)
            f.write(content)
            return
    def create_graph(self):
        self.graph = Graph()
        self.graph.bind("dcterms", DCTERMS)
        self.graph.bind("rdf", RDF)
        self.graph.bind("rdfs", RDFS)
        self.graph.bind("dc", DC)
        self.namespaces["HAB"] = Namespace("https://diglib.hab.de/")
        self.graph.bind("hab", self.namespaces["HAB"])
        self.namespaces["SC"] = Namespace("http://iiif.io/api/presentation/2#")
        self.graph.bind("sc", self.namespaces["SC"])
        self.namespaces["EXIF"] = Namespace("http://www.w3.org/2003/12/exif/ns#")
        self.graph.bind("exif", self.namespaces["EXIF"])
        self.namespaces["SVCS"] = Namespace("http://rdfs.org/sioc/services#")
        self.graph.bind("svcs", self.namespaces["SVCS"])   
        self.namespaces["OA"] = Namespace("http://www.w3.org/ns/oa#")
        self.graph.bind("oa", self.namespaces["OA"])
        self.namespaces["DCTYPES"] = Namespace("http://purl.org/dc/dcmitype/")
        self.graph.bind("dctypes", self.namespaces["DCTYPES"])
        return(True)