#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import httpx
import json
import functools
from datetime import date
from lib import localsql as lsql
logging.basicConfig(level=logging.INFO)

class Resolver():
    def __init__(self, file_name = None):
        self.folder = "drucke"
        self.year_init = 1998
        self.dc = lsql.DataConnection("year_digi")
        self.dc_fail = lsql.DataConnection("digi_fail")
    def get_digi_year(self, norm_sig, folder = None):
        if folder != None:
            self.folder = folder  
        res = self.dc.sql_request(f"SELECT year FROM main WHERE norm_sig LIKE '{norm_sig}' and folder LIKE '{self.folder}'")
        try:
            year = res[0][0]
        except:
            logging.info(f"Nicht gefunden: {self.folder}/{norm_sig}")
        else:
            return(year)
        res_fail = self.dc_fail.sql_request(f"SELECT * FROM main WHERE norm_sig LIKE '{norm_sig}' and folder LIKE '{self.folder}'")
        if len(res_fail) > 0:
            logging.info(f"{self.folder}/{norm_sig} wurde bereits negativ geprüft")
            return(None)
        year = date.today().year
        while year >= self.year_init:
            test_url = self.make_link(norm_sig, year, folder)
            r = httpx.get(test_url)
            if r.status_code == 200:
                ins_action = self.dc.sql_action(f"INSERT INTO main VALUES ('{norm_sig}', '{self.folder}', '{year}')")
                if self.dc.rows_affected > 0:
                    logging.info(f"Es wurden die Werte {norm_sig}, {self.folder}, {year} in die Datenbank {self.dc.file_name} eingefügt.")
                    return(str(year))
            year -= 1
        ins_action = self.dc_fail.sql_action(f"INSERT INTO main VALUES ('{norm_sig}', '{self.folder}')")
        if self.dc_fail.rows_affected > 0:
            logging.info(f"Es wurden die Werte {norm_sig}, {self.folder} in die Datenbank {self.dc_fail.file_name} eingefügt.")
        return(None)
    def make_link(self, norm_sig, year, folder = None, page = None):
        if folder != None:
            self.folder = folder
        if page == None:
            page = "00001"
        link = f"https://image.hab.de/iiif/images/{self.folder}/{norm_sig}/{year}_standard_original/{norm_sig}_{page}.jp2/info.json"
        return(link)
    def make_default(self, norm_sig, year, folder, page):
        link = f"https://image.hab.de/iiif/images/{self.folder}/{norm_sig}/{year}_standard_original/{norm_sig}_{page}.jp2/full/max/0/default.jpg"
        return(link)        
    def forget_item(self, norm_sig, folder = None):
        if folder != None:
            self.folder = folder
        sql = f"DELETE FROM main WHERE norm_sig LIKE '{norm_sig}' and folder LIKE '{self.folder}'"
        self.dc.sql_action(sql)
        self.dc_fail.sql_action(sql)
        if self.dc.rows_affected > 0:
            logging.info(f"Wert {self.folder}/{norm_sig} aus Datenbank year_digi gelöscht")
        if self.dc_fail.rows_affected > 0:
            logging.info(f"Wert {self.folder}/{norm_sig} aus Datenbank digi_fail gelöscht")            
    def get_failed(self):
        sql = "SELECT * FROM main"
        res = self.dc_fail.sql_request(sql)
        return(res)
    def get_all(self):
        sql = "SELECT * FROM main"
        res = self.dc.sql_request(sql)
        return(res)
    def close(self):
        self.dc.close()
        self.dc_fail.close()

# Das Caching bringt nicht viel, da es nur zur Laufzeit des Programms verfügbar ist. => Datenbank o. ä. einbinden
@functools.lru_cache(maxsize=10000)
def get_dimensions(url):
    #url = f"https://image.hab.de/iiif/images/{folder}/{norm_sig}/{year}_standard_original/{norm_sig}_{page}.jp2/info.json"
    r = httpx.get(url)
    if r.status_code != 200:
        logging.error(f" {url} konnte nicht geladen werden")
        return(None)
    parsed_json = json.loads(r.text)
    try:
        dim = (parsed_json["width"], parsed_json["height"])
    except:
        #logging.error(f" Abmessungen zu {folder}/{norm_sig}, Seite {page} konnten nicht geladen werden")
        return(None)
    return(dim)
        
    
        