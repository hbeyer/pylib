#!/usr/bin/python3
# -*- coding: utf-8 -*-

import glob
import urllib.request as ul
import xml.etree.ElementTree as et
import re

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
		self.data = {}
		self.getData()
		self.persons = []
		self.copies = []
		self.places = []
		self.publishers = []
		try:
			self.ppn = self.data["003@"]["01"]["0"].pop(0)
		except:
			self.ppn = ""
		try:
			self.bbg = self.data["002@"]["01"]["0"].pop(0)
		except:
			self.bbg = ""
		try:
			self.vd17 = self.data["006W"]["01"]["0"]
		except:
			self.vd17 = []
		bud = None
		try:
			bud = self.data["001A"]["01"]["0"].pop(0)
		except:
			pass
		else:
			self.isilRec = bud.split(":").pop(0)
			try:
				self.dateRec = bud.split(":").pop(1)
			except:
				pass
		try:
			self.catRule = self.data["010E"]["01"]["e"].pop(0)
		except:
			self.catRule = "rak"
		try:
			self.title = self.data["021A"]["01"]["a"].pop(0)
		except:
			self.title = ""
		try:
			self.title = self.title + ". " + self.data["021A"]["01"]["d"].pop(0)
		except:
			pass
		try:
			self.resp = self.data["021A"]["01"]["h"].pop(0)
		except:
			self.resp = ""
		try:
			self.lang = self.data["010@"]["01"]["a"]
		except:
			self.lang = []
		try:
			self.langOrig = self.data["010@"]["01"]["c"]
		except:
			self.langOrig = []
		self.gatt = []
		try:
			gatDict = self.data["044S"]
		except:
			pass
		else:
			for occ in gatDict:
				try:
					self.gatt.extend(gatDict[occ]["a"])
				except:
					pass
		# Funktioniert igendwie nicht
		#self.gatt = map(lambda term: re.sub("!.+!", "", str(term)), self.gatt)
		try:
			self.pages = self.data["034D"]["01"]["a"].pop(0)
		except:
			self.pages = ""
		self.normPages = 0
		if self.pages != "":
			self.getNormP()
		try:
			self.format = self.data["034I"]["01"]["a"].pop(0)
		except:
			self.format = ""
		try:
			self.vd16m = self.data["006L"]["01"]["0"]
		except:
			self.vd16m = []
		try:
			self.date = self.data["011@"]["01"]["a"].pop(0)
		except:
			self.date = ""
		self.digi = []
		try:
			digiDict = self.data["017D"]
		except:
			pass
		else:
			for key in digiDict:
				try:
					self.digi.extend(digiDict[key]["u"])
				except:
					pass
		self.loadPersons()
		self.loadCopies()
		self.loadPlaces()
		self.loadPublishers()
	def __str__(self):
		ret = "record: PPN " + self.ppn + ", VD17: " + "|".join(self.vd17) + ", Jahr: " + self.date
		return(ret)
	def getData(self):
		fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield")
		occDict = {}
		for fn in fields:
			tag = fn.get("tag")
			occ = fn.get("occurrence")
			if occ == None:
				try:
					occDict[tag] += 1
				except:
					occDict[tag] = 1
				occ = str(occDict[tag]).zfill(2)
			children = fn.findall("*")
			for ch in children:
				code = ch.get("code")
				try:
					self.data[tag][occ][code].append(ch.text)
				except:
					try:
						self.data[tag][occ][code] = [ch.text]
					except:
						try:
							self.data[tag][occ] = { code: [ch.text] }
						except:
							try:
								self.data[tag] = { occ: { code: [ch.text] } }
							except:
								pass
	def loadPersons(self):
		subfields = ["7", "A", "D", "P", "L", "a", "d", "p", "l"]
		creatorData = self.getNestedValues("028A", subfields)
		if creatorData != {}:
			per = Person()
			per.role = "creator"
			per.importPICA(creatorData)
			self.persons.append(per)
		creator2Data = self.getNestedValuesOcc("028B", subfields)
		for row in creator2Data:
			per = Person()
			per.role = "creator"
			per.importPICA(row)
			self.persons.append(per)	
		subfields.append("B")
		contributorData = self.getNestedValuesMulti("028C", subfields)
		for row in contributorData:
			per = Person()
			per.role = "contributor"
			per.importPICA(row)
			self.persons.append(per)
	def loadCopies(self):
		copyData = self.getNestedValuesOcc("209A", ["a"])
		copyDataLib1 = self.getNestedValuesOcc("201D", ["0"])
		copyDataLib2 = self.getNestedValuesOcc("202D", ["a"])
		count = 0
		for row in copyData:
			sm = ""
			isil = ""
			try:
				sm = row["a"]
			except:
				pass
			try:
				isil = copyDataLib2[count]["a"]
			except:
				try:
					isil = copyDataLib1[count]["0"].split(":").pop(0)
				except:
					pass
			cop = Copy(sm)
			cop.isil = isil
			self.copies.append(cop)
			count += 1
	def loadPlaces(self):
			placeData = self.getNestedValuesMulti("033D", ["p", "4"])
			for row in placeData:
				try:
					placeName = row["p"]
				except:
					continue
				else:
					try:
						rel = row["4"]
					except:
						rel = None
					self.places.append(Place(placeName, rel))
	def loadPublishers(self):
		subfields = ["7", "A", "D", "P", "L", "E", "M", "a", "d", "p", "l", "e", "m"]
		pubData = self.getNestedValuesMulti("028A", subfields)
		for row in pubData:
			pub = Person()
			pub.role = "publisher"
			pub.importPICA(row)
			self.publishers.append(pub)
	def getNormP(self):
		if self.catRule == "rda":
			extract = re.findall(r"(\d+) (ungezählte )?Seiten", self.pages)
			for group in extract:
				self.normPages += int(group[0])
			extract = re.findall(r"(\d+) (ungezählte |ungezähltes )?Bl[äa]tt", self.pages)
			for group in extract:
				self.normPages += int(group[0])*2
			extract = re.findall(r"(\d+) B[oö]gen", self.pages)
			for group in extract:
				self.normPages += int(group)*2				
			return(True)
		else:
			extract = re.findall(r"(\d+) S\.?", self.pages)
			for group in extract:
				self.normPages += int(group)
			extract = re.findall(r"\[?(\d+)\]? Bl\.?", self.pages)
			for group in extract:
				self.normPages += int(group)*2
		return(True)			
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
					row[sf.lower()] = fieldNode.text
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
					row[sf.lower()] = fieldNode.find("{info:srw/schema/5/picaXML-v1.0}subfield[@code='" + sf + "']").text
				except:
					pass
			ret.append(row)
		return(ret)
	def getProvenances(self, occurrence):
		fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='244Z'][@occurrence='" + occurrence + "']/{info:srw/schema/5/picaXML-v1.0}subfield[@code='9']/../{info:srw/schema/5/picaXML-v1.0}subfield[@code='a']")
		if fields:
			return([field.text.strip() for field in fields])
		return([])

class Person:
	def __init__(self):
		self.persName = ""
		self.forename = ""
		self.surname = ""
		self.namePart1 = ""
		self.namePart2 = ""
		self.gnd = ""
		self.dateBirth = None
		self.dateDeath = None
	def __str__(self):
		if self.forename and self.surname:
			self.persName = self.surname + ", " + self.forename
		elif self.namePart1 and namePart2:
			self.persName = self.namePart1 + " " + self.namePart2
		elif self.namePart1:
			self.persName = self.namePart1
		ret = self.persName
		try:
			ret.append(" GND: " + self.gnd)
		except:
			pass
		return(ret)
	def importPICA(self, row):
		try:
			self.forename = row["d"]
		except:
			pass
		try:
			self.surname = row["a"]
		except:
			pass
		try:
			self.namePart1 = row["p"]
		except:
			pass
		try:
			self.namePart2 = row["l"]
		except:
			pass
		try:
			self.role = row["b"]
		except:
			pass
		try:
			self.gnd = row["7"].replace("gnd/", "")
		except:
			pass
		try:
			self.dateBirth = row["e"]
		except:
			pass
		try:
			self.dateDeath = row["m"]
		except:
			pass			
		return(True)

class Copy:
	def __init__(self, sm, provenances = [], epn = None):
		self.place = ""
		self.bib = ""
		self.isil = ""
		self.sm = sm
		self.provenances = provenances
		self.epn = epn
	def __str__(self):
		ret = "Signatur: " + self.sm
		if self.isil != "":
			ret = "ISIL: " + self.isil + " " + ret
		if self.provenances != []:
			ret += ", Provenienz: " + ";".join(self.provenances)
		if self.epn != None:
			ret += ", EPN: " + self.epn
		return(ret)

class Place:
	def __init__(self, placeName, rel = None):
		self.placeName = placeName
		self.getty = None
		self.geoNames = None
		self.gnd = None
		self.rel = rel