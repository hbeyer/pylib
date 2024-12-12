#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import logging
import urllib.request as ur
import urllib.parse as up
from lib import cache

class Request_Lobid():
    def __init__(self, base = ""):
        self.base = base
        self.size = "100"
        self.format = "json"
        self.url = ""
        self.query = ""
        self.query_enc = ""
        self.num_found = 0
        self.data = []
    def make_url(self):
        self.url = self.base + "?q=" + self.query_enc + "&size=" + self.size + "&format=" + self.format
        return(True)
    def get_num(self):
        lc = cache.CacheLobid()
        text = lc.get_content(self.query, 0, 100)
        try:
            self.data = json.loads(text)
        except:
            #logging.error(f"Fehler beim Laden des Ergebnisses für {self.query}")
            pass
        try:      
            self.num_found = self.data["totalItems"]
        except:
            #logging.error(f"Fehler beim Laden des Ergebnisses für {self.query}")
            return(None)
        #else:
            #logging.info(f"{self.num_found} Treffer für {self.query}")        
        return(True)
    def prepare(self, query):
        self.query = query
        if self.query == "":
            return(None)
        self.query_enc = up.quote(self.query)
        self.make_url()
        self.get_num()
        return(True)
    def get_result(self):
        return(None)

# Eine Suche in der vom hbz bereitgestellten lobid-gnd, s. http://lobid.org/gnd/
class Request_GNDLobid(Request_Lobid):
    def __init__(self, size = None):
        super().__init__()
        self.base = "http://lobid.org/gnd/search"
        if size != None:
            self.size = size
    def get_num(self):
        lc = cache.CacheGNDLobid()
        text = lc.get_content(self.url, self.query)
        try:
            self.data = json.loads(text)
        except:
            #logging.error(f"Fehler beim Laden des Ergebnisses für {self.query}")
            pass
        try:      
            self.num_found = self.data["totalItems"]
        except:
            #logging.error(f"Fehler beim Laden des Ergebnisses für {self.query}")
            return(None)
        #else:
            #logging.info(f"{self.num_found} Treffer für {self.query}")        
        return(True)
    def get_result(self):
        result = []
        try:
            first = self.data["member"][0]
        except:
            #logging.error(f"Keine Daten geladen.")
            return(result)
        for mem in self.data["member"]:
            if "Person" not in mem["type"]:
                continue
            result.append(self.extract_info(mem))
        return(result)
    def extract_info(self, mem):
        info = { 
            "preferredName" : mem["preferredName"], 
            "gnd" : mem["gndIdentifier"], 
            "variantNames" : "", 
            "dateOfBirth" : "", 
            "dateOfDeath" : "", 
            "placeOfBirth" : "", 
            "placeOfDeath" : "", 
            "periodOfActivity" : "", 
            "biographicalOrHistoricalInformation" : "", 
            "gender" : "",
            "wikidata" : ""
        }
        try:
            info["variantNames"] = ";".join(mem["variantName"]).replace('"', '').replace("„", "").replace("“", "")
        except:
            pass
        try:
            info["dateOfBirth"] = mem["dateOfBirth"][0]
        except:
            pass
        try:
            info["dateOfDeath"] = mem["dateOfDeath"][0]
        except:
            pass
        try:
            info["placeOfBirth"] = mem["placeOfBirth"][0]["label"]
        except:
            pass
        try:
            info["placeOfDeath"] = mem["placeOfDeath"][0]["label"]
        except:
            pass
        try:
            info["periodOfActivity"] = "; ".join(mem["periodOfActivity"])
        except:
            pass
        try:
            info["biographicalOrHistoricalInformation"] = "; ".join(mem["biographicalOrHistoricalInformation"])
        except:
            pass
        try:
            info["gender"] = mem["gender"][0]["label"]
        except:
            pass
        try:
            sameAsList = mem["sameAs"]
        except:
            pass
        else:
            wikidataSet = set();
            for data in sameAsList:
                if "wikidata" in data["id"]:
                    wikidataSet.add(data["id"].replace("http://www.wikidata.org/entity/", ""))
            info["wikidata"] = "|".join(wikidataSet)
        return(info)

# Eine Suche, bei der eine GND-Nummer übergeben wird
class Request_GNDLobid_ID(Request_GNDLobid):
    def __init__(self, size = None):
        super().__init__()
    def make_url(self):
        self.url = f"https://lobid.org/gnd/{self.query_enc}.json"
        return(True)
    def get_num(self):
        lc = cache.CacheGNDLobid()
        text = lc.get_content(self.url, self.query)
        try:
            self.data = json.loads(text)
        except:
            #logging.error(f"Fehler beim Laden des Ergebnisses für {self.query}")
            pass
        if len(self.data) > 0:
            self.num_found = 1
            return(True)
        return(False)
    def get_result(self):
        result = []
        if self.num_found == 0:
            return(result)
        result.append(self.extract_info(self.data))
        return(result)
