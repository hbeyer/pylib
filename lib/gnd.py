#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import json
import re
import urllib.request as ur

class ID:
    base = 'http://hub.culturegraph.org/entityfacts/'
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
    def get_info(self):
        ad = self.get_auth_data()
        if json == None:
            return(None)
        data = json.loads(ad)
        persData = {}
        propp = ["preferredName", "dateOfBirth", "dateOfDeath", "biographicalOrHistoricalInformation"]
        for p in propp:
            try:
                persData[p] = data[p]
            except:
                logging.info(f"Kein {p} gefunden")
        propp2 = ["placeOfBirth", "placeOfDeath"]
        for p in propp2:
            try:
                persData[p] = data[p][0]["preferredName"]
            except:
                logging.info(f"Kein {p} gefunden")
        try:
            persData["gender"] = data["gender"]["label"]
        except:
            logging.info(f"Kein {p} gefunden")
        return(persData)
    def get_auth_data(self):
        if self.valid == True:
            url = self.base + self.gnd
            fileobject = ur.urlopen(url)
            string = fileobject.read()
            return(string)
        else:
            logging.error(f"Ungültige GND-Nummer {gnd}")
            return(None)