#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as et
import os
import os.path as op

class Request_unAPI:
    def __init__(self, base = "http://unapi.k10plus.de/?id=gvk:ppn:"):
        self.folder = "downloads/unapi"
        self.base = base
        self.url = ""
        self.query_pica = ""
        self.query_pica_enc = ""
        self.numFound = 0
        os.makedirs(self.folder, exist_ok = True)
    def prepare(self, ppn, format = "picaxml"):
        self.query_pica = ppn
        self.format = format
        self.ppn = ppn
        self.url = self.base + self.ppn + "&format=" + self.format
    def download(self, folder = ""):
        path = self.folder + "/" + self.ppn + "-" + self.format + ".xml"
        if op.exists(path) == False:
            ur.urlretrieve(self.url, path)
        if op.exists(path):
            return(True)