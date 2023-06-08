#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import json
import logging
import re
import urllib.request as ur
import xml.etree.ElementTree as et
from lib import cache
from lib import isil as il
from lib import xmlserializer as xs
from lib import romnumbers as rn
from lib import provenance as prv

class Lobid:
    def __init__(self):
        self.base = "https://lobid.org/resources/"
        self.url = ""
        self.data = None
        hits = 0
        self.identifiers = []
        self.size_sets = 1000
    def prepare(self, query):
        self.query = query
        self.url = f"{self.base}search?q={query}&format=json"
        try:
            response = ur.urlopen(self.url, None, 10).read()
        except:
            logging.error(f"Keine Antwort von {self.url}")
            return(None)
        self.data = json.loads(response)
        try:
            self.hits = int(self.data["totalItems"])
        except:
            logging.error(f"totalItems nicht gefunden")
            return(None)
        return(self.hits)
    def get_identifiers(self):
        cl = cache.CacheLobid()
        if self.hits == 0:
            return([])
        start = 0
        while start * self.size_sets <= self.hits:
            response = cl.get_json(self.query, start, self.size_sets)
            start += 1
            if response == None:
                logging.error(f"Keine Antwort bei Treffer {str(start * self.size_sets)}")
                continue
            ids = extract_identifiers(response)
            if ids != None:
                self.identifiers.extend(ids)
            else:
                logging.error("Keine Identifier gefunden")
        return(self.identifiers)
    def download(self):
        cm = cache.CacheMarcHBZ()
        for count, id in enumerate(self.identifiers):
            xml = cm.get_xml(id)
        logging.info(f"Marc-Download abgeschlossen für {self.query}, {str(count)} Datensätze heruntergeladen")
        return(True)

def extract_identifiers(data_str):
    data = json.loads(data_str)
    try:
        ids = [mem["almaMmsId"] for mem in data["member"]]
    except:
        return(None)
    return(ids)
