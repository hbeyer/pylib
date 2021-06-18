#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as et
import os.path as op
import glob

class Request_OAI:
    def __init__(self):
        self.fileName = "downloadOAI"
        self.base = "http://oai.hab.de/"
        self.namespace = "{http://www.openarchives.org/OAI/2.0/}"
        self.prefix = "oai_dc"
        self.folder = ""
        self.url = ""
        self.numFound = 0
        self.resumptionToken = None
        self.id = None
        self.setSpec = ""
    def makeURL(self):
        setSpec = self.setSpec
        if setSpec != "":
            setSpec = "&set=" + setSpec
        if self.id == None and self.resumptionToken == None:
            return(self.base + "?verb=ListRecords&metadataPrefix=" + self.prefix + setSpec)
        if self.resumptionToken == None:
            return(self.base + "?verb=GetRecord&metadataPrefix=" + self.prefix + "&identifier=" + self.id)
        return(self.base + "?verb=ListRecords&resumptionToken=" + self.resumptionToken)
    def download(self, folder = "", prefix = "", setSpec = ""):
        self.folder = folder    
        self.setSpec = setSpec
        self.folder = self.folder.strip("/") + "/"
        if prefix != "":
            self.prefix = prefix
        url = self.makeURL()
        path = self.makePath()
        fo = ur.urlopen(url, None, 60)
        tree = et.parse(fo)
        if op.exists(path) == False:
            print("Speichern: " + url)
            tree.write(path, "utf-8", True)
        self.getResumptionToken(tree)
        while self.resumptionToken != None:
            url = self.makeURL()
            path = self.makePath()
            fo = ur.urlopen(url, None, 60)
            tree = et.parse(fo)
            if fo == None:
                break
            if op.exists(path) == False:
                print("Speichern: " + url)
                tree.write(path, "utf-8", True)
            self.getResumptionToken(tree)
    def getResumptionToken(self, tree):
        root = tree.getroot()
        rtt = root.findall(".//" + self.namespace + "resumptionToken")
        try:
            self.resumptionToken = rtt[0].text
        except:
            self.resumptionToken = None
        return(self.resumptionToken)
    def makePath(self):
        path = self.folder + self.fileName + "-" + self.prefix
        if self.resumptionToken != None:
            path = path + "-" + self.resumptionToken
        return(path + ".xml")

class Request_VKK(Request_OAI):
    def __init__(self):
        super().__init__()
        self.base = "http://www.virtuelles-kupferstichkabinett.de/service/oai/"
        self.fileName = "downloadVKK"