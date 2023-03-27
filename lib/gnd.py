#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import json
import re
import urllib.request as ur

class ID:
    def __init__(self, gnd):
        self.gnd = str(gnd)[0:10]
        test = re.match('[0-9X-]{8,10}', self.gnd)
        self.valid = False
        if test != None:
            self.valid = True
        else:
            logging.error(f"Ungültige GND-Nummer {gnd}")
    def __str__(self):
        if self.valid == True:
            return(self.gnd)
        return(f"{self.gnd} (ungültig)")
    def get_info(self, cache):
        if cache.__class__.__name__ != "CacheGND":
            logging.error("Kein CacheGND übergeben")
            return(None)
        ad = cache.get_json(self.gnd)
        if json == None:
            return(None)
        data = json.loads(ad)
        persData = {}
        propp = ["preferredName", "dateOfBirth", "dateOfDeath", "biographicalOrHistoricalInformation"]
        for p in propp:
            try:
                persData[p] = replace_diacr(data[p])
            except:
                #logging.info(f"Kein {p} gefunden")
                pass
        try:
            persData["variantNames"] = "; ".join(data["variantName"])
        except:
            #logging.info(f"Kein variantName gefunden")
            pass
        propp2 = ["placeOfBirth", "placeOfDeath"]
        for p in propp2:
            try:
                persData[p] = data[p][0]["preferredName"]
            except:
                #logging.info(f"Kein {p} gefunden")
                pass
        try:
            persData["gender"] = data["gender"]["label"]
        except:
            #logging.info(f"Kein {p} gefunden")
            pass
        persData["familialRelationship"] = []
        try:
            fam_rel = data["familialRelationship"]
        except:
            pass
        else:        
            for pers_fam in fam_rel:
                try:
                    persData["familialRelationship"].append({"name" : pers_fam["preferredName"], "id" : pers_fam["@id"].replace("https://d-nb.info/gnd/", ""), "type" : pers_fam["relationship"]})
                except:
                    logging.error(f"Unvollständige Relation: {str(pers_fam)}")
        persData["relatedPerson"] = []
        try:
            pers_rel = data["relatedPerson"]
        except:
            pass
        else:
            for pers_rel in pers_rel:
                try:
                    persData["relatedPerson"].append({"name" : pers_rel["preferredName"], "id" : pers_rel["@id"].replace("https://d-nb.info/gnd/", ""), "type" : pers_rel["relationship"]})
                except:
                    logging.error(f"Unvollständige Relation: {str(pers_rel)}")
        return(persData)

class Person:
    def __init__(self, id, cache):
        self.gndid = ID(id)
        if self.gndid.valid == True:
            self.id = id
        self.name = ""
        self.var_names = []
        self.gender = ""
        self.date_birth = None
        self.place_birth = ""
        self.date_death = None
        self.place_death = ""
        self.places_activity = []
        self.info = ""
        self.relations = []
        self.get_data(cache)
    def get_data(self, cache):
        pers_data = self.gndid.get_info(cache)
        try:
            self.name = pers_data["preferredName"]
        except:
            pass
        try:
            self.var_names = pers_data["variantNames"].split("; ")
        except:
            pass            
        try:
            self.date_birth = pers_data["dateOfBirth"]
        except:
            pass
        try:
            self.date_death = pers_data["dateOfDeath"]
        except:
            pass
        try:
            self.place_birth = pers_data["placeOfBirth"]
        except:
            pass
        try:
            self.place_death = pers_data["placeOfDeath"]
        except:
            pass
        try:
            self.gender = pers_data["gender"]
        except:
            pass
        for rel in pers_data["familialRelationship"]:
            self.relations.append(rel)
        for rel in pers_data["relatedPerson"]:
            self.relations.append(rel)        
        
def replace_diacr(string):
    return(string.replace("ö", "ö").replace("ò", "ò").replace("̈a", "ä").replace("à", "à"))