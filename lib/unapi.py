#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.parse as up
import urllib.request as ur
import xml.etree.ElementTree as et
import os.path as op

class Request_unAPI:
	def __init__(self, base = "http://unapi.k10plus.de/?id=gvk:ppn:"):
		self.fileName = "downloadUnAPI"
		self.base = base
		self.url = ""
		self.query_pica = ""
		self.query_pica_enc = ""
		self.numFound = 0
	def prepare(self, ppn, format = "picaxml"):
		self.query_pica = ppn
		self.format = format
		self.ppn = ppn
		self.url = self.base + self.ppn + "&format=" + self.format
		fileobject = ur.urlopen(self.url, None, 10)
		tree = et.parse(fileobject)
		root = tree.getroot()
		nbs = root.findall('.//{http://docs.oasis-open.org/ns/search-ws/sruResponse}numberOfRecords')
		for ele in nbs:
			self.numFound = int(ele.text)
			self.url = self.make_URL(500)
			break
		return(self.numFound)
	def download(self, folder = ""):
		self.folder = folder
		path = self.folder + "/" + self.ppn + "-" + self.format + ".xml"
		if op.exists(path) == False:
			ur.urlretrieve(self.url, path)
		if op.exists(path):
			print("PPN " + self.ppn + " in " + self.format + " heruntergeladen nach " + self.folder)