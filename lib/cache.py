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
        except OSError as error:
            logging.info(f"Ordner {self.folder} bereits vorhanden")
    def get_content(self, url, id):
        path = self.folder + "/" + id
        if op.exists(path) != True:
            ur.urlretrieve(url, path)
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
            logging.info(f"Programm pausiert für 5 Minuten")
            sleep(300)
            return(None)
        else:
            return(response)
            
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