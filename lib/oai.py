#!/usr/bin/python3
# -*- coding: utf-8 -*-

#import urllib.parse as up
#import urllib.request as ur
import httpx
import xml.etree.ElementTree as et
import os.path as op
import glob
import os
import logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

class Request_OAI:
    def __init__(self, folder = None, prefix = None, set_spec = None):
        self.folder = folder or "downloads/oai/"
        self.folder += "" if self.folder.endswith("/") else "/"
        self.prefix = prefix or "oai_dc"
        self.set_spec = set_spec or ""
        self.fileName = "downloadOAI"
        self.base = "https://oai.hab.de/"
        self.namespace = "{http://www.openarchives.org/OAI/2.0/}"
        self.url = ""
        self.numFound = 0
        self.resumptionToken = None
        self.id = None
        self.setSpec = ""
        logging.info(f"{self.__class__.__name__} erzeugt.\nBasis-URL: {self.base}\nOrdner: {self.folder}\nFormat: {self.prefix}\nNamespace: {self.namespace}\nWeiter geht es mit der Methode prepare()")        
    def prepare(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
            logging.info(f"Ordner {self.folder} wurde angelegt")
        self.url = self.make_url()
        self.get_num_found()
        logging.info(f"{self.numFound} Records vorhanden\nLade alle mit der Methode download()")
    def make_url(self):
        spec = self.set_spec
        if spec != "":
            spec = "&set=" + spec
        if self.id == None and self.resumptionToken == None:
            return(self.base + "?verb=ListRecords&metadataPrefix=" + self.prefix + spec)
        if self.resumptionToken == None:
            return(self.base + "?verb=GetRecord&metadataPrefix=" + self.prefix + "&identifier=" + self.id)
        return(self.base + "?verb=ListRecords&resumptionToken=" + self.resumptionToken)
    def download(self, limit = None):
        cnt = 0
        while True:
            url = self.make_url()
            path = self.make_path()
            logging.info("Download: " + url)
            with httpx.stream("GET", url, timeout=60) as response:
                response.raise_for_status()
                if op.exists(path):
                    logging.info(f"Pfad {path} existiert schon.")
                else:
                    logging.info("Speichern: " + url)

                    with open(path, "wb") as file:
                        for chunk in response.iter_bytes():
                            file.write(chunk)
            cnt += 1
            self.get_resumption_token(path)
            if self.resumptionToken is None:
                logging.info(f"Vorgang fehlendem resumptionToken abgebrochen")
                break
            if limit != None:
                if cnt > limit:
                    break
                    logging.info(f"Vorgang wegen Limit {limit} vorzeitig abgebrochen")
    def get_resumption_token(self, path):
        try:
            tree = et.parse(path)
            root = tree.getroot()
            rtt = root.findall(".//" + self.namespace + "resumptionToken")
            self.resumptionToken = rtt[0].text if rtt else None
        except et.ParseError:
            self.resumptionToken = None
        return self.resumptionToken
    def get_num_found(self):
        with httpx.stream("GET", self.url, timeout=60) as response:
            response.raise_for_status()
            data = response.read()
        try:
            root = et.fromstring(data)
            rtt = root.findall(".//" + self.namespace + "resumptionToken")
            self.numFound = int(rtt[0].attrib["completeListSize"]) if rtt else 0
        except (et.ParseError, KeyError, TypeError, ValueError):
            self.numFound = 0
        return self.numFound
    def make_path(self):
        path = self.folder + self.fileName + "-" + self.prefix
        if self.resumptionToken != None:
            path = path + "-" + self.resumptionToken
        return(path + ".xml")        
        
class Request_VKK(Request_OAI):
    def __init__(self):
        super().__init__()
        self.base = "http://www.virtuelles-kupferstichkabinett.de/service/oai/"
        self.fileName = "downloadVKK"
        
class Request_ERARA(Request_OAI):
    def __init__(self):
        super().__init__()
        self.base = "https://www.e-rara.ch/oai"
        self.fileName = "downloadERARA"        