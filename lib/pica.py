#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import urllib.request as ul
import os
import xml.etree.ElementTree as et

class Reader:
	def __init__(self, path):
		self.path = path
		self.recs = []
	def getRecs(self, file):
		tree = et.parse(file)
		root = tree.getroot()
		recs = root.findall('.//{http://docs.oasis-open.org/ns/search-ws/sruResponse}record')
		if recs:
			return(recs)
		print("Keine Datensätze")
		return([])

class downloadReader(Reader):
	def __init__(self, path):
		super().__init__(path)
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
	
class webReader(Reader):
	def __init__(self, path):
		super().__init__(path)
		try:
			file = ul.urlopen(self.path)
		except:
			print(self.path + " ist keine funktionierende URL")
		else:
			self.recs = self.getRecs(file)

class Record:
	def __init__(self, node):
		self.node = node
		self.copies = []
		try:
			self.ppn = self.getValues("003@", "0").pop(0)
		except:
			self.ppn = ""
		try:			
			self.bbg = self.getValues("002@", "0").pop(0)
		except:
			self.bbg = ""
		self.vd17 = self.getValues("006W", "0")
		try:
			self.title = self.getValues("021A", "a").pop(0)
		except:
			self.title = ""
		try:
			self.pages = self.getValues("034D", "a").pop(0)
		except:
			self.pages = ""
		self.altTitles = self.getValues("027a", "a")
		self.vd16m = self.getValues("006L", "0")
		try:
			self.date = self.getValues("011@", "a").pop(0)
		except:
			self.date = ""
		self.shelfmarks = self.getValues("209A", "a")
		self.loadCreators()
	def __str__(self):
		ret = "record: PPN " + self.ppn + ", VD17: " + "|".join(self.vd17) + ", Jahr: " + self.date
		return(ret)
	def getCopies(self):
		goon = True
		occ = 1
		while goon == True:
			occstr = str(occ).zfill(2)
			sigg = self.getRepValues("209A", "a", occstr)
			epn = self.getRepValues("203@", "0", occstr)
			provv = self.getProvenances(occstr)
			try:
				copy = Copy(sigg.pop(0), provv, epn.pop(0))
			except:
				goon = False
			else:
				self.copies.append(copy)
				occ += 1
	def loadCreators(self):
		subfields = ["7", "A", "D", "P", "L", "a", "d", "p", "l"]
		creatorData = self.getNestedValues("028A", subfields)
		creator2Data = self.getNestedValuesOcc("028B", subfields)
		subfields.append("B")
		# Das Folgende funktioniert so nicht, weil es hier keine occurrence gibt
		contributorData = self.getNestedValuesMulti("028C", subfields)
		print(contributorData)
	def getValues(self, field, subfield):
		fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='" + field + "']/{info:srw/schema/5/picaXML-v1.0}subfield[@code='" + subfield + "']")
		if fields:
			return([field.text.strip() for field in fields])
		return([])
	def getRepValues(self, field, subfield, occurrence):
		fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='" + field + "'][@occurrence='" + occurrence + "']/{info:srw/schema/5/picaXML-v1.0}subfield[@code='" + subfield + "']")
		if fields:
			return([field.text.strip() for field in fields])
		return([])
	def getNestedValues(self, field, subfields, occurrence = None):
		if occurrence != None:
			fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='" + field + "'][@occurrence='" + occurrence + "']/{info:srw/schema/5/picaXML-v1.0}subfield")
		else:
			fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='" + field + "']/{info:srw/schema/5/picaXML-v1.0}subfield")
		row = {}
		for fieldNode in fields:
			for sf in subfields:
				if fieldNode.attrib["code"] == sf:
					row[sf] = fieldNode.text
		return(row)
	def getNestedValuesOcc(self, field, subfields):
		ret = []
		goon = True
		occ = 1
		while goon == True:
			occstr = str(occ).zfill(2)
			vall = self.getNestedValues(field, subfields, occstr)
			if vall == {}:
				goon = False
				return(ret)
			else:
				ret.append(vall)
				occ += 1
		return(ret)
	def getNestedValuesMulti(self, field, subfields):
		ret = []
		fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='" + field + "']")
		for fieldNode in fields:
			row = {}
			for sf in subfields:
				try: 
					row[sf] = fieldNode.find("{info:srw/schema/5/picaXML-v1.0}subfield[@code='" + sf + "']").text
				except:
					pass
			ret.append(row)
		return(ret)
	def getProvenances(self, occurrence):
		fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='244Z'][@occurrence='" + occurrence + "']/{info:srw/schema/5/picaXML-v1.0}subfield[@code='9']/../{info:srw/schema/5/picaXML-v1.0}subfield[@code='a']")
		if fields:
			return([field.text.strip() for field in fields])
		return([])

class Copy:
	def __init__(self, sm, provenances = [], epn = None):
		self.sm = sm
		self.provenances = provenances
		self.epn = epn
	def __str__(self):
		ret = "Signatur: " + self.sm
		try:
			ret += ", Provenienz: " + ";".join(self.provenances)
		except:
			pass
		try:
			ret += ", EPN: " + self.epn
		except:
			pass
		return(ret)
