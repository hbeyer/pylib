#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import pica
from lib import sru
from lib import unapi as ua
from lib import xmlreader as xr
from lib import shelfmark as sm
from lib import dataset as ds
import xml.etree.ElementTree as et
import urllib.request as ur
import re
import os

class Harvester():
	def __init__(self, ppnO, folder = "downloads"):
		self.ppnO = ppnO
		self.folder = folder
		self.path = self.folder + "/" + self.ppnO
		try:
			os.mkdir(self.path)
		except:
			pass
		reqU = ua.Request_unAPI()
		reqU.prepare(ppnO, "picaxml")
		reqU.download(self.path)
		reader = xr.unAPIReader(self.path + "/" + self.ppnO + "-" + "picaxml.xml")
		node = reader.node
		self.recO = pica.Record(node)
		self.sig = self.recO.copies[0].sm
		self.normSig = re.search("http://diglib.hab.de/inkunabeln/(.+)/start.htm", self.recO.digi).group(1)
		sigSRU = self.sig.replace("(", "").replace(")", "").replace(" ", "+")
		req = sru.Request_HAB()
		req.prepare("pica.sgb=" + sigSRU)
		wr = xr.webReader(req.url, tag = "record", namespace = "http://docs.oasis-open.org/ns/search-ws/sruResponse")
		for node in wr:
			rc = pica.RecordInc(node)
			if rc.bbg[0] == "A":
				self.recA = rc
				reqU.prepare(self.recA.ppn)
				reqU.download(self.path)
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
		self.meta.addEntry("description", ds.Entry("Digitalisierte Inkunabel aus dem Bestand der Herzog August Bibliothek Wolfenbüttel", "ger"))
		self.meta.addEntry("rights", ds.Entry("CC BY-SA 3.0"))
		self.meta.addEntry("rights", ds.Entry("http://diglib.hab.de/copyright.html"))
		self.meta.addEntry("source", ds.Entry("Wolfenbüttel, Herzog August Bibliothek, " + self.sig))
		if self.recA.gw != "":
			self.meta.addEntry("relation", ds.Entry(self.recA.gw))
		if self.recA.istc != "":
			self.meta.addEntry("relation", ds.Entry(self.recA.istc))
	def loadFiles(self):
		urlMets = "http://oai.hab.de/?verb=GetRecord&metadataPrefix=mets&identifier=oai:diglib.hab.de:ppn_" + self.ppnO
		try:
			ur.urlretrieve(urlMets, self.path + "/mets.xml")
		except:
			print("Laden der METS fehlgeschlagen")
		urlStruct = "http://diglib.hab.de/inkunabeln/" + self.normSig + "/facsimile.xml"
		try:
			ur.urlretrieve(urlStruct, self.path + "/facsimile.xml")
		except:
			print("Laden der facsimile.xml fehlgeschlagen")
		urlTranscr = "http://diglib.hab.de/inkunabeln/" + self.normSig + "/tei-struct.xml"
		try:
			ur.urlretrieve(urlStruct, self.path + "/tei-struct.xml")
		except:
			print("Keine tei-struct.xml gefunden")