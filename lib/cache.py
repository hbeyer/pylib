#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import urllib.parse as up
import os.path as op
import urllib.request as ur
from time import sleep

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
        path = self.folder + "/" + id
        if op.exists(path) != True:
            try:
                ur.urlretrieve(url, path)
            except:
                return(None)
        file = open(path, "r", encoding="utf-8")
        content = file.read()
        return(content)

class CacheGND(Cache):
    folder = "cache/gnd"
    def __init__(self):
        super().__init__()
    def get_json(self, id):
        url = f"http://hub.culturegraph.org/entityfacts/{id}"
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
        path = f"{self.folder}/{query}_{start}-{str(start + size)}"
        if op.exists(path) != True:
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
