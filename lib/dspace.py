#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import pica
from lib import sru
from lib import xmlreader as xr
from lib import dataset as ds
import xml.etree.ElementTree as et
import urllib.request as ur
import re
import os
import json

class Harvester():
	def __init__(self, ppnO, folder = "downloads", diglib = "inkunabeln"):
		self.ppnO = ppnO
		self.folder = folder
		self.diglib = diglib
		file = ur.urlopen("http://unapi.k10plus.de/?id=gvk:ppn:" + self.ppnO + "&format=picaxml")
		tree = et.parse(file)
		node = tree.getroot()		
		self.recO = pica.Record(node)
		self.sig = self.recO.copies[0].sm
		search = re.search("http://diglib.hab.de/([^/]+)/([^/]+)/start.htm", self.recO.digi)
		try:
			self.diglib = search.group(1)
		except:
			pass
		self.normSig = search.group(2)
		self.path = self.folder + "/" + self.normSig
		self.recA = None
		sigSRU = self.sig.replace("(", "").replace(")", "").replace(" ", "+")
		req = sru.Request_HAB()
		req.prepare("pica.sgb=" + sigSRU)
		wr = xr.webReader(req.url, tag = "record", namespace = "http://docs.oasis-open.org/ns/search-ws/sruResponse")
		for node in wr:
			rc = pica.RecordInc(node)
			if rc.bbg[0] == "A":
				self.recA = rc
				self.ppnA = self.recA.ppn
		if self.recA == None:
			self.recA = self.recO
		self.imageList = []
	def go(self):
		self.makeFolder()
		self.downloadXML()
		self.downloadImages()
		self.extractMetadata()
		self.saveMetadata()
	def makeFolder(self):
		if os.path.exists(self.path):
			pass
		else:
			os.mkdir(self.path)
	def downloadXML(self):
		urlO = "http://unapi.k10plus.de/?id=gvk:ppn:" + self.ppnO + "&format=picaxml"
		try:
			ur.urlretrieve(urlO, self.path + "/o-aufnahme.xml")
		except:
			print("Laden der O-Aufnahme fehlgeschlagen")
		try:
			ur.urlretrieve("http://unapi.k10plus.de/?id=gvk:ppn:" + self.ppnA + "&format=picaxml", self.path + "/a-aufnahme.xml")
		except:
			print("Laden der A-Aufnahme fehlgeschlagen")		
		urlMets = "http://oai.hab.de/?verb=GetRecord&metadataPrefix=mets&identifier=oai:diglib.hab.de:ppn_" + self.ppnO
		try:
			ur.urlretrieve(urlMets, self.path + "/mets.xml")
		except:
			print("Laden der METS fehlgeschlagen")
		urlStruct = "http://diglib.hab.de/" + self.diglib + "/" + self.normSig + "/facsimile.xml"
		try:
			ur.urlretrieve(urlStruct, self.path + "/facsimile.xml")
		except:
			print("Laden der facsimile.xml fehlgeschlagen")
		urlTranscr = "http://diglib.hab.de/" + self.diglib + "/" + self.normSig + "/tei-struct.xml"
		try:
			ur.urlretrieve(urlStruct, self.path + "/tei-struct.xml")
		except:
			print("Keine tei-struct.xml gefunden")
	def downloadImages(self):
		file = open(self.path + "/facsimile.xml")
		tree = et.parse(file)
		root = tree.getroot()
		for gr in root:
			imName = gr.attrib["url"].split("/").pop()
			self.imageList.append(imName)
		for im in self.imageList:
			#path = "\\\\maserver.hab.de\\Auftraege\\Master\\" + self.diglib + "\\" + self.normSig + "\\" + im.replace("jpg", "tif")
			#ur.urlretrieve(path, self.path + "/" + im.replace("jpg", "tif"))
			path = "http://diglib.hab.de/" + self.diglib + "/" + self.normSig + "/" + im
			ur.urlretrieve(path, self.path + "/" + im)
	def extractMetadata(self):
		self.meta = ds.DatasetDC()
		self.meta.addEntry("identifier", ds.Entry(self.recO.digi))
		self.meta.addEntry("format", ds.Entry("Online resource", "eng"))
		self.meta.addEntry("type", ds.Entry("Digitized book", "eng"))
		self.meta.addEntry("title", ds.Entry(self.recA.title))
		self.meta.addEntry("date", ds.Entry(self.recA.date))
		for pers in self.recA.persons:
			pers.makePersName()
			if pers.role == "creator":
				self.meta.addEntry("creator", ds.Entry(pers.persName, None, "GND", pers.gnd))
			else:
				self.meta.addEntry("contributor", ds.Entry(pers.persName, None, "GND", pers.gnd))
		for pub in self.recA.publishers:
			pub.makePersName()
			self.meta.addEntry("publisher", ds.Entry(pub.persName, None, "GND", pub.gnd))
		for lng in self.recA.lang:
			self.meta.addEntry("language", ds.Entry(lng))
		for sub in self.recA.subjects:
			self.meta.addEntry("subject", ds.Entry(sub))
		if self.diglib == "inkunabeln" or int(self.recA.date) <= 1500:
			self.meta.addEntry("description", ds.Entry("Digitalisierte Inkunabel aus dem Bestand der Herzog August Bibliothek Wolfenbüttel", "ger"))
		else:
			self.meta.addEntry("description", ds.Entry("Digitalisierter Druck aus dem Bestand der Herzog August Bibliothek Wolfenbüttel", "ger"))
		self.meta.addEntry("rights", ds.Entry("CC BY-SA 3.0"))
		self.meta.addEntry("rights", ds.Entry("http://diglib.hab.de/copyright.html"))
		self.meta.addEntry("source", ds.Entry("Wolfenbüttel, Herzog August Bibliothek, " + self.sig))
		try:
			self.meta.addEntry("relation", ds.Entry(self.recA.gw))
		except:
			pass
		try:
			self.meta.addEntry("relation", ds.Entry(self.recA.istc))
		except:
			pass
	def saveMetadata(self):
		meta = self.meta.toList()
		with open(self.path + "/metadata.json", "w") as target:
			json.dump(meta, target, indent=2, ensure_ascii=False)