#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import sqlite3
import shutil
import urllib.parse as up
import httpx
import os.path as op
import urllib.request as ur
from time import sleep
from lib import image_resolver as ir

class Cache:
    folder = "cache/default"
    def __init__(self, folder = None):
        if isinstance(folder, str):
            self.folder = folder
        try:
            os.mkdir(self.folder)
        except:
            pass
    def get_content(self, url, id):
        path = f"{self.folder}/{id}"
        if op.exists(path) == True:
            #file = open(path, "r" encoding="utf-8")
            file = open(path, "r")
            content = file.read()
            return(content)
        r = httpx.get(url)
        if r.status_code != 200:
            logging.error(f" {url} konnte nicht geladen werden")
            return(None)
        response = r.text
        with open(path, "w") as f:
            f.write(response)
        #ur.urlretrieve(self.url, path)
        return(response)
    def _get_content(self, url, id):
        path = self.folder + "/" + id
        if op.exists(path) != True:
            try:
                ur.urlretrieve(url, path)
            except:
                return(None)
        file = open(path, "r", encoding="utf-8")
        content = file.read()
        return(content)

class CacheSRU_O(Cache):
    def __init__(self):
        super().__init__("cache/sru_o")
    def get_xml(self, url, id):
        try:
            response = self.get_content(url, id)
        except:
            logging.error(f"Kein Download von {url} möglich")
            return(None)
        else:
            return(response)        
        
class CacheStruct(Cache):
    def __init__(self):
        super().__init__("cache/struct")
    def get_xml(self, sig, folder_wdb = None):
        if folder_wdb == None:
            folder_wdb = "drucke"
        url = f"https://diglib.hab.de/{folder_wdb}/{sig}/tei-struct.xml"
        try:
            response = self.get_content(url, sig)
        except:
            logging.error(f"Kein Download von {url} möglich")
            return(None)
        else:
            if response == None:
                logging.error(f"Kein Download von {url} möglich")
            return(response)   
            
class CacheFacsimile(Cache):
    def __init__(self):
        super().__init__("cache/facs")
    def get_xml(self, sig, folder_wdb = None):
        if folder_wdb == None:
            folder_wdb = "drucke"
        url = f"https://diglib.hab.de/{folder_wdb}/{sig}/facsimile.xml"
        try:
            response = self.get_content(url, sig)
        except:
            logging.error(f"Kein Download von {url} möglich")
            return(None)
        else:
            if response == None:
                logging.error(f"Kein Download von {url} möglich")
            return(response)          
"""            
class CachePICA(Cache):
    folder = "cache/pica"
    def __init__(self):
        super().__init__()
    def get_xml(self, ppn):
        url = f""
        try:
            response = self.get_content(url, id)
        except:
            logging.error(f"Kein Download von {url} möglich")
            #logging.info(f"Programm pausiert für 5 Minuten")
            #sleep(300)
            return(None)
        else:
            return(response)
"""            

class CacheGESA(Cache):
    folder = "cache/gesa"
    def __init__(self):
        super().__init__()
    def get_html(self, id):
        url = f"https://www.online.uni-marburg.de/fpmr/php/gs/id2.php?lang=de&id[]={id}"
        try:
            response = self.get_content(url, id)
        except:
            logging.error(f"Kein Download von {url} möglich")
            return(None)
        else:
            return(response)
            
class CacheLobid(Cache):
    folder = "cache/lobid"
    def __init__(self):
        super().__init__()
    def get_json(self, query, start, size):
        self.make_url(query, start, size)
        try:
            response = self.get_content(query, start, size)
        except:
            logging.error(f"Kein Download von {self.url} möglich")
            return(None)
        else:
            return(response)        
    def get_content(self, query, start, size):
        path = f"{self.folder}/{query.replace(':', '_')}_{start}-{str(start + size)}"
        if op.exists(path) != True:
            self.make_url(query, str(start), str(size))
            print(path)
            ur.urlretrieve(self.url, path)
        file = open(path, "r", encoding="utf-8")
        content = file.read()
        return(content)
    def make_url(self, query, start, size):
        self.url = f"https://lobid.org/resources/search?q={query}&format=json&from={str(start)}&size={str(size)}"
        return(True)

class CacheMarcHBZ(Cache):
    folder = "cache/marc-hbz"
    def __init__(self):
        super().__init__()
    def get_xml(self, id):
        url = f"https://alma.lobid.org/marcxml/{id}"
        path = f"{self.folder}/{id}.xml"
        if op.exists(path) != True:
            ur.urlretrieve(url, path)
        file = open(path, "r", encoding="utf-8")
        content = file.read()
        return(content)

class CacheGNDLobid(Cache):
    folder = "cache/gnd-lobid"
    def __init__(self):
        super().__init__()

class CacheSQLite:
    def __init__(self, file_name = None):
        self.file_name = "cache"
        if file_name != None:
            self.file_name = file_name
        self.conn = sqlite3.connect(self.file_name + ".db")
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("SELECT * FROM main LIMIT 5")
        except:
            sql = f"CREATE TABLE main (url type UNIQUE, result)"
            self.cursor.execute(sql)
            self.conn.commit()
    def get(self, url):
        sql = f"SELECT * FROM main WHERE url LIKE \"{url}\""
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        try:
            ret = res[0][1]
        except:
            logging.info(f" Laden aus {url}")
            data = self.get_dataset(url)
            if data != None:
                self.insert_dataset(data, url)
            try:
                ret = ",".join(data)
            except:
                return(None)
            else:
                return(ret)
        else:
            return(ret)
    def get_dataset(self):
        return(None)
    def close(self):
        self.conn.close()
    def show_content(self, limit = None):
        if limit == None:
            limit = 100
        sql = "SELECT * FROM main"
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        cnt = 0
        print(f"Inhalt der Datenbank {self.file_name}.db (Maximum: {limit} Datensätze):")
        while row != None:
            print(row)
            cnt += 1
            if cnt > limit:
                break
            row = self.cursor.fetchone()
    def forget_everything(self):
        old_file = self.file_name + ".db"
        new_file = self.file_name + "_backup.db"
        shutil.copyfile(old_file, new_file)
        logging.info(f" Backup erstellt: {new_file}")
        sql = "DELETE FROM main"
        self.cursor.execute(sql)
        self.conn.commit()
        
class CacheImageDimensions(CacheSQLite):
    def __init__(self):
        super().__init__("image_dimensions")
    def get_dataset(self, url):
        dimensions = ir.get_dimensions(url)
        try:
            width, height = dimensions
        except:
            logging.error(f" Nicht vorhandenes Bild: {url}")
            return(None)
        return([str(width), str(height)])
    def insert_dataset(self, data, url):
        # Auf Dubletten prüfen?
        sql = "INSERT INTO main VALUES (?, ?)"
        row = [url, ",".join(data)]
        self.cursor.execute(sql, row)
        self.conn.commit()