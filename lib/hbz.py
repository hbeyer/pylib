#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import json
import logging
import re
import httpx
import os
import xml.etree.ElementTree as et
from pathlib import Path
from lib import cache

# Größere Treffermengen, dazu einfach Format jsonl anfordern. S. Lobid.download_jsonl
# Beispiel: https://lobid.org/resources/search?q=publication.startDate:[1500+TO+1600]&format=jsonl

class Lobid:
    def __init__(self):
        self.base = "https://lobid.org/resources/"
        self.url = ""
        self.data = None
        num_hits = 0
        self.identifiers = []
        self.size_sets = 1000
        self.folder = "downloads/hbz"
        self.from_item = 0
        self.size = 1000
        self.client = httpx.Client(timeout=30.0)
    def prepare(self, query):
        self.query = query
        self.url = f"{self.base}search?q={self.query}&format=json&size=1"
        data_binary = self.load_content()
        self.data = json.loads(data_binary)
        try:
            self.num_hits = int(self.data["totalItems"])
        except:
            logging.error(f"totalItems nicht gefunden")
            return(None)
        logging.info(f"{self.num_hits} Datensätze gefunden")
        if self.num_hits > 10000:
            logging.info(f"Diese Treffermenge muss mit der Methode download_jsonl() als Bulk geladen werden.")
        return(self.num_hits)
    def download_json(self, folder = None):
        if folder is not None:
            self.folder = folder
        os.makedirs(self.folder, exist_ok = True)           
        from_item = self.from_item
        while from_item < self.num_hits:
            self.url = f"{self.base}search?q={self.query}&format=json&from={from_item}&size={self.size}"
            logging.info(f"Download ab {from_item}")
            data_binary = self.load_content()
            with open(f"{self.folder}/download_{str(from_item)}.json", "wb") as file:
                file.write(data_binary)
                logging.info(f"Treffer {from_item} bis {from_item + self.size} heruntergeladen")
            from_item += self.size
        logging.info(f"Heruntergeladen bis Treffer {str(from_item)}")
        return(True)
    def download_jsonl(self, folder = None):
        if folder is not None:
            self.folder = folder
        os.makedirs(self.folder, exist_ok = True)
        self.url = f"{self.base}search?q={self.query}&format=jsonl"
        data_binary = self.load_content() 
        with open(f"{self.folder}/download.jsonl", "wb") as file:
            file.write(data_binary)
    def load_content(self):
        try:
            r = self.client.get(self.url)
            r.raise_for_status()  # wirft Exception bei HTTP-Fehlern
        except httpx.HTTPError as e:
            logging.error(f"{self.url} konnte nicht geladen werden: {e}")
            return(None)
        if not r.content:
            return(None)        
        return(r.content)
    def download_marc(self):
        cm = cache.CacheMarcHBZ()
        for count, id in enumerate(self.identifiers):
            xml = cm.get_xml(id)
        logging.info(f"Marc-Download abgeschlossen für {self.query}, {str(count)} Datensätze heruntergeladen")
        return(True)

class LobidReader:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.members = []        
        return
    def read(self):
        self.paths = list(self.folder.glob("*.json"))
        for path in self.paths:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            try:
                self.members.extend(data["member"])
            except:
                print(f"Problem bei {path}")
        return(len(self.members))

class LobidReaderBulk(LobidReader):
    def __init__(self, folder):
        super().__init__(folder)
        return
    def read(self):
        self.paths = list(self.folder.glob("*.jsonl"))
        for path in self.paths:
            with open(path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    self.members.append(data)
        return(len(self.members))
        
class Record:
    def __init__(self, data):
        self.data = data
        self.id_hbz = data.get("almaMmsId")
        self.purl = data.get("id")
        self.title = data.get("title")
        self.get_persons()
        self.alt_title = data.get("alternativeTitle")
        self.title_addition = data.get("otherTitleInformation")
        self.type = ";".join(data.get("type", []))
        self.bib_level = data.get("bibliographicLevel").get("label")
        self.extent = data.get("extent")
        notes = data.get("note")
        self.note = ""
        if notes is not None:
            self.note = ";".join(notes)
        publication = data.get("publication", [])
        language = data.get("language")
        if language:
            self.languages = ";".join([lan["label"] for lan in language])
        else:
            self.languages = ""
        if publication:
            publication = publication[0]

            self.date = publication.get("dateStatement")
            self.places = publication.get("location")
            self.publishers = publication.get("publishedBy")
        else:
            logging.warning("Keine Daten unter 'publication'")
            self.date = ""
            self.places = ""
            self.publishers = ""
        self.get_copies()
        self.get_works()
        self.digi = []
        digi_data = self.data.get("fulltextOnline")
        if digi_data is not None:
            for row in digi_data:
                self.digi.append(row.get("id"))
    def get_persons(self):
        self.persons = []
        contributions = self.data.get("contribution")
        if contributions is None:
            return(False)
        for contr in contributions:
            self.persons.append(Person(contr))
        return(True)
    def get_copies(self):
        self.copies = []
        items = self.data.get("hasItem")
        if items is None:
            return(False)
        for item in items:
            self.copies.append(Copy(item))
        return(True)
    def get_works(self):
        self.works = []
        work_data = self.data.get("containsExampleOfWork")
        if work_data is None:
            return(False)
        for work_d in work_data:
            self.works.append(Work(work_d))
        return(True)
    def __str__(self):
        ret = f"Eintrag hbz {self.id_hbz}, Titel: {str(self.title)}, Datum: {str(self.date)}, PURL: {self.purl}"
        return(ret)
        
class Person:
    def __init__(self, contribution):
        try:
            self.name = contribution.get("agent")["label"]
        except:
            self.name = ""
        try:
            self.gnd = contribution.get("agent")["gndIdentifier"]
        except:
            self.gnd = ""
        try:
            self.role = contribution.get("role")["label"]
        except:
            self.role = ""
    def __str__(self):
        ret = f"{self.role}: {self.name}"
        if self.gnd:
            ret = ret + f"({self.gnd})"
        return(ret)
        
class Copy:
    def __init__(self, item):
        self.shelfmark = item.get("callNumber")
        try:
            self.isil = item.get("heldBy").get("isil")
        except:
            self.isil = ""
        try:
            self.bib = item.get("heldBy").get("label")
        except:
            self.bib = ""
    def __str__(self):
        ret = f"{self.bib} ({self.isil}), {self.shelfmark}"
        return(ret)
        
class Work:
    def __init__(self, work):
        self.title = work.get("label")
        self.title = "" if self.title is None else self.title
        self.creator = work.get("creatorOfWork")
        self.creator = "" if self.creator is None else self.creator
        types = work.get("type")
        if types is not None:
            self.types = ";".join(types)
        self.types = "" if self.types is None else self.types
    def __str__(self):
        ret = f"{self.title}"
        if self.creator:
            ret = f"{self.creator}: {ret}"
        ret = f"{ret} ({self.types})"
        return(ret)