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
		self.url = self.make_URL()
		fileobject = ur.urlopen(self.url, None, 10)
		tree = et.parse(fileobject)
		root = tree.getroot()
		nbs = root.findall('.//{http://docs.oasis-open.org/ns/search-ws/sruResponse}numberOfRecords')
		for ele in nbs:
			self.numFound = int(ele.text)
			self.url = self.make_URL(500)
			break
		return(self.numFound)
	def make_URL(self, maxRecords = 1, start = 1):
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
			url = self.make_URL(500, count)
			if op.exists(path) == False:
				ur.urlretrieve(url, path)
			if op.exists(path):
				print("Download " + str(countFiles) + " erledigt")
			count += 500
			countFiles += 1

class Request_K10plus(Request_SRU):
	def __init__(self):
		super().__init__()
		self.base = 'http://sru.k10plus.de/k10plus'
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
		self.base = 'http://sru.gbv.de/opac-de-23'
		self.fileName = "SRU_HAB"