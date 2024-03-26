#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as et
import os.path as op

class Request_SRU:
    def __init__(self, base = "", version = "2.0"):
        self.fileName = "downloadSRU"
        self.base = base
        self.url = ""
        self.version = version
        self.query_pica = ""
        self.query_pica_enc = ""
        self.numFound = 0
    def prepare(self, query_pica, format = "picaxml"):
        self.query_pica = query_pica
        self.format = format
        self.query_pica_enc = self.query_pica.replace(", ", ",")
        #self.query_pica_enc = self.query_pica_enc.replace(",", "%2C")
        self.query_pica_enc = up.quote(self.query_pica_enc)
        self.url = self.make_url()
        fileobject = ur.urlopen(self.url, None, 10)
        tree = et.parse(fileobject)
        root = tree.getroot()
        nbs = root.findall('.//{http://docs.oasis-open.org/ns/search-ws/sruResponse}numberOfRecords')
        for ele in nbs:
            self.numFound = int(ele.text)
            self.url = self.make_url(500)
            break
        return(self.numFound)
    def make_url(self, maxRecords = 1, start = 1):
        url = self.base + "?version=" + self.version + "&operation=searchRetrieve&query=" + self.query_pica_enc + "&maximumRecords=" + str(maxRecords) + "&startRecord=" + str(start) + "&recordSchema=" + self.format
        return(url)
    def download(self, folder = "", fileName = False):
        self.folder = folder
        if fileName != False:
            self.fileName = fileName
        count = 1
        countFiles = 1
        while count <= self.numFound:
            path = self.folder + "/" + self.fileName + "-" + str(countFiles) + ".xml"
            url = self.make_url(500, count)
            if op.exists(path) == False:
                ur.urlretrieve(url, path)
            if op.exists(path):
                print("Download " + str(countFiles) + " erledigt")
            count += 500
            countFiles += 1

class Request_K10plus(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/opac-de-627'
        self.fileName = "downloadK10plus"

class Request_VD17(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/vd17'
        self.fileName = "downloadVD17"

class Request_VD18(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/vd18'
        self.fileName = "downloadVD18"

class Request_HAB(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/opac-de-23'
        self.fileName = "SRU_HAB"
        
class Request_Greifswald(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/opac-de-9'
        self.fileName = "SRU_Greifswald"

class Request_IKAR(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/ikar'
        self.fileName = "SRU_IKAR"
        
class Request_HPB(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/hpb'
        self.fileName = "SRU_HPB"
        
class Request_OGND(Request_SRU):
    def __init__(self):
        super().__init__()
        self.base = 'http://sru.k10plus.de/ognd'
        self.fileName = "SRU_OGND"

def chunk(iterable, max_size):
    """
    This function splits an iterable into chunks of the specified maximum size.
    :param iterable: The iterable to be split.
    :param max_size: The maximum size of each chunk.
    :return: A list of chunks.
    """
    chunks = []
    current_chunk = []
    for item in iterable:
        if len(current_chunk) < max_size:
            current_chunk.append(item)
        else:
            chunks.append(current_chunk)
            current_chunk = [item]
    if current_chunk:
        chunks.append(current_chunk)
    return chunks
