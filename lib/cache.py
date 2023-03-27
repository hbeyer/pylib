#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import os
import urllib.parse as up
import os.path as op
import urllib.request as ur

class Cache:
    folder = "cache/default"
    def __init__(self, folder = None):
        if isinstance(folder, str):
            self.folder = folder
        try:
            os.mkdir(self.folder)
        except OSError as error:
            logging.info(error)
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
        json = self.get_content(url, id)
        return(json)