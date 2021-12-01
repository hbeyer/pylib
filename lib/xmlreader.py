#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import urllib.request as ul
import xml.etree.ElementTree as et
import re

class Reader:
    def __init__(self, path, tag = "record", namespace = ""):
        self.tag = tag
        self.namespace = namespace
        if self.namespace != "":
            self.namespace = "{" + self.namespace + "}"        
        self.path = path
        self.recs = []
    def getRecs(self, file):
        tree = et.parse(file)
        root = tree.getroot()
        recs = root.findall(".//" + self.namespace + self.tag)
        if recs:
            return(recs)
        print("Keine Datensätze")
        return([])

class downloadReader(Reader):
    def __init__(self, path, tag = "", namespace = ""):
        super().__init__(path, tag, namespace)        
        self.files = glob.glob(self.path + "/*.xml")
        self.unread = self.files
    def readFile(self):
        while self.unread:
            path = self.unread.pop(0)
            try:
                file = open(path, "r", encoding="utf-8")
            except:
                pass
            else:
                return(self.getRecs(file))
        return(None)
    def __iter__(self):
        self.recs = self.readFile()
        return(self)
    def __next__(self):
        try:
            rec = self.recs.pop(0)
        except:
            self.recs = self.readFile()
            try:
                rec = self.recs.pop(0)
            except:
                raise StopIteration
            else: 
                return(rec)
        else:
            return(rec)

class OAIDownloadReader(downloadReader):
    def __init__(self, path):
        super().__init__(path, "record", "http://www.openarchives.org/OAI/2.0/")

class SRUDownloadReader(downloadReader):
    def __init__(self, path):
        super().__init__(path, "record", "http://docs.oasis-open.org/ns/search-ws/sruResponse")

class webReader(Reader):
    def __init__(self, path, tag = "", namespace = ""):
        super().__init__(path, tag, namespace)
        try:
            file = ul.urlopen(self.path)
        except:
            print(self.path + " ist keine funktionierende URL")
        else:
            self.recs = self.getRecs(file)
    def __iter__(self):
        return(self)
    def __next__(self):
        try:
            rec = self.recs.pop(0)
        except:
            raise StopIteration
        return(rec)

class unAPIReader(Reader):
    def __init__(self, path, tag = "", namespace = ""):
        super().__init__(path, tag, namespace)
        file = open(path, "r")
        tree = et.parse(file)
        self.node = tree.getroot()