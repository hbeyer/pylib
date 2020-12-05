#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

class Shelfmark:
	def __init__(self, whole):
		self.whole = whole.strip()
		self.root = ""
		self.bareRoot = ""
		self.collection = ""
		self.part = ""
		self.group = ""
		self.number = ""
		self.format = ""
		self.volume = ""		
		self.valid = False		
		extract = re.search(r"(A:|H:|M:|Bibel-S\.|Ältere Einblattdrucke|aeltere einblattdrucke|Alv\.|Cod\. Guelf\.|Xylogr|Druckfragm|Wa |Xb |Wt |We |Schulenb|Xd )", self.whole)
		conc = { 
			"A:":"A", 
			"H:":"H", 
			"M:":"M", 
			"Bibel-S.":"BS", 
			"aeltere einblattdrucke":"AEB", 
			"Ältere Einblattdrucke":"AEB", 
			"Alv.":"Alv", 
			"Xylogr":"XYL", 
			"Druckfragm":"FGM", 
			"Wa ":"NE", 
			"Xb ":"NE", 
			"Wt ":"NE", 
			"We ": "BR", 
			"Schulenb":"SLB", 
			"Xd ":"DUB"
		}
		try:
			self.collection = conc[extract.group(1)]
		except:
			return(None)
		extract = re.search(r"(.+)\s\(([0-9a-d]{1,2})\)$", self.whole)
		try:
			self.part = extract.group(2)				
		except:
			pass
		try:
			self.root = extract.group(1)
		except:
			self.root = self.whole
		if self.collection == "AEB":
			self.root = self.root.replace("aelt", "Ält")
			self.root = self.root.replace("einbl", "Einbl")
		if self.collection in ["A", "H", "M"]:
			self.bareRoot = self.root.replace(self.collection + ": ", "")
		else:
			self.bareRoot = self.root
		if self.collection and self.root:
			self.valid = True
	def __str__(self):
		ret = self.root
		if self.part:
			ret += ' (' + self.part + ')'
		return(ret)
	def getFormat(self):
		extract = re.search(r"2°|4°|8°|12°|16°", self.whole)
		try:
			self.format = extract.group(0)
		except:
			return(None)
		else:
			return(self.format)
	def getGroup(self):
		if self.collection == "A":
			extract = re.search(r"Theol|Jur|Hist|Bell|Pol|Oec|Eth|Med|Geogr|Astr|Phys|Geom|Arit|Poet|Log|Rhet|Gram|Quod", self.whole)
			conc = {"Gram":"Gramm", "Arit":"Arith", "Astr":"Astron"}
			try:
				self.group = extract.group(0)
			except:
				return(None)
			try:
				self.group = conc[self.group]
			except:
				pass
			self.group = self.group + "."
		elif self.collection == "M":
			extract = re.search(r"[ABCDEFGHJKLMNOPQRSTUVZ][a-z]N?", self.whole)
			try:
				self.group = extract.group(0)
			except:
				return(None)
		elif self.collection == "H":
			extract = re.search(r"\s([A-Z]|QuH|Y[a-z])\s", self.whole)
			try:
				self.group = extract.group(1)
			except:
				return(None)
		return(self.group)
	def getNumber(self):
		if self.collection == "H":
			extract = re.search(r"H: ([A-Z]|QuH|Y[a-z])\s([0-9]+[a-z]{0,2}\*?)\.?(2°|4°|8°|12°)?", self.whole)
			try:
				self.number = extract.group(2)
			except:
				 return(None)
		elif self.collection == "A":
			extract = re.search(r"A: ([0-9\.-a-z]+)\s[A-Z][a-z]+\.", self.whole)
			try:
				self.number = extract.group(1)
			except:
				 return(None)
		elif self.collection == "M":
			extract = re.search(r"M: ([A-Z][a-z]|QuN)\s((gr\.-2°|2°|4°|8°|12°)\s)?((Mischbd\.|Sammelbd\.|Kapsel)\s)?([0-9\.]+)", self.whole)
			try:
				self.number = extract.group(6)
			except:
				return(None)
		elif self.collection == "XYL":
			extract = re.search(r"([0-9]+)\sXyl", self.whole)
			try:
				self.number = extract.group(1)
			except:
				return(None)
		elif self.collection == "AEB":
			extract = re.search(r"drucke\s([0-9]+)", self.whole)
			try:
				self.number = extract.group(1)
			except:
				return(None)
		else:
			extract = re.search(r"\s([0-9\.]+[a-z]?)[^°]", self.whole)
			try:
				self.number = extract.group(1)
			except:
				extract = re.search(r"\s([0-9\.]+[a-z]?)$", self.whole)
				try:
					self.number = extract.group(1)
				except:
					return(None)
		return(self.number)
	def getVolumeNo(self):
		extract = re.search(r":([0-9\.-]{1,4})", self.whole)
		try:
			self.volume = extract.group(1)
		except:
			pass
class StructuredShelfmark(Shelfmark):
		def __init__(self, whole):
			super().__init__(whole)			
			self.getFormat()
			self.getGroup()
			self.getNumber()
			self.getVolumeNo()
			self.sortable = self.makeSortable()
		def __str__(self):
			ret = "Bestand: " + self.collection + ", Klasse: " + self.group + ", Nummer: " + self.number
			if self.format:
				ret = ret + ", Format: " + self.format
			if self.part:
				ret = ret + ", Stücktitel: " + self.part
			return(ret)
		def sortableNum(self, num):
			parts = num.split(".")
			parts = self.separateLetters(parts)
			parts = [p.zfill(4) for p in parts]
			return(".".join(parts))
		def separateLetters(self, parts):
			ret = []
			for p in parts:
				extract = re.search(r"([0-9]+)([a-z]+)", p)
				try:
					sp = [extract.group(1), extract.group(2)]
				except:
					sp = [p]
				ret.extend(sp)
			return(ret)
		def translateGroup(self):
			if self.collection != "A":
				return(self.group)
			conc = {
				"Theol.":"01Theol",
				"Jur.":"02Jur",
				"Hist.":"03Hist",
				"Bell.":"04Bell",
				"Pol.":"05Pol",
				"Oec.":"06Oec",
				"Eth.":"07Eth",
				"Med.":"08Med",
				"Geogr.":"09Geog",
				"Astron.":"10Astr",
				"Phys.":"11Phys",
				"Geom.":"12Geom",
				"Arith.":"13Arit",
				"Poet.":"14Poet",
				"Log.":"15Log",
				"Rhet.":"16Rhet",
				"Gramm.":"17Gram",
				"Quod.":"18Quod"
			}
			if self.group in conc:
				return(conc[self.group]) 
			else:
				print("Fehler bei " + self.whole + "!")
				return(self.group)
		def makeSortableRoot(self):
			sortColl = self.collection.ljust(3, "0")
			sortFormat = "00"
			if self.format != "" and self.collection != "A":
				sortFormat = self.format.replace("°", "").zfill(2)
			sortGroup = "000000"
			if self.group:
				sortGroup = self.translateGroup()
				sortGroup = sortGroup.strip(".").ljust(6, "0")
			res = [sortColl, sortGroup, sortFormat, self.sortableNum(self.number), self.sortableNum(self.volume)]
			return(".".join(res))
		def makeSortable(self):
			sr = self.makeSortableRoot()
			if self.part:
				sr += self.part.zfill(4)
			return(sr)
class ShelfmarkList():
	def __init__(self, content = []):
		self.content = []
		self.volumeDict = {}
		for sm in content:
			self.addSM(sm)
		self.volumeList = []
	def addSM(self, sm):
		if isinstance(sm, StructuredShelfmark):
			self.content.append(sm)
	def makeVolumes(self):
		for shm in self.content:
			if shm.part:
				try:
					self.volumeDict[shm.bareRoot].parts.append(shm.part)
				except:
					self.volumeDict[shm.bareRoot] = Volume(shm.bareRoot, shm.makeSortableRoot(), [shm.part])
			else:
				self.volumeDict[shm.bareRoot] = Volume(shm.bareRoot, shm.makeSortableRoot())
		self.makeVolumeList()
	def makeVolumeList(self):
		self.volumeList = [self.volumeDict[vol] for vol in self.volumeDict]
		self.volumeList = sorted(self.volumeList, key=lambda v:v.sortable)
	def getByRoot(self, root):
		try:
			return(self.volumeDict[root])
		except:
			return(None)
class Volume():
	def __init__(self, bareRoot, sortable, parts = []):
		self.root = bareRoot
		self.sortable = sortable
		self.parts = []
		self.partStr = ""
		for part in parts:
			self.parts.append(part)
	def makePartStr(self):
		self.parts = sorted(self.parts, key=lambda p:p.zfill(3))
		self.partStr = ", ".join(self.parts)
	def __str__(self):
		self.makePartStr()
		ret = self.root
		if self.partStr:
			ret += " (" + self.partStr + ")"
		return(ret)

def convertVD16(old):
	if old[0:1] == "\"":
		old = old + ")"
	new = old.strip("\"")
	if new.find("Helmst") > 0 or new.find("QuH") == 0:
		new = "H: " + new
	elif re.search(r"Theol|Jur|Hist|Bell|Pol|Oec|Eth|Med|Geogr|Astr|Phys|Geom|Arit|Poet|Log|Rhet|Gram|Quod", new):
		new = "A: " + new
	elif re.match(r"[ABCDEFGHJKLMNOPQRSTUVZ][a-z]N? ", new):
		new = "M: " + new
	#elif new.find("Alv") == 0:
	#	new = "S. " + new
	new = new.replace("(", " (")
	new = new.replace("Alv ", "Alv.: ")
	new = new.replace("Lpr.Stolb.", "Lpr. Stolb. ")
	new = new.replace("Bibel-S.", "Bibel-S. ")
	new = new.replace("Helmst.Dr.", "Helmst. Dr.")
	new = new.replace("°H", "° H")
	try:
		letter = re.search(r"(\s)([a-z])", new).group(2)
	except:
		pass
	else:
		space = re.search(r"(\s)([a-z])", new).group(1)
		new = new.replace(space + letter, letter)
	try:
		num = re.search(r"([a-z]{2})\.([0-9])", new).group(2)
	except:
		pass
	else:
		letter = re.search(r"([a-z])\.([0-9])", new).group(1)
		new = new.replace(letter + "." +  num, letter + ". " +  num)
	try:
		numlet = re.search(r"([0-9][a-z]{1,2})\. ([0-9])", new).group(1)
	except:
		pass
	else:
		num = re.search(r"([0-9][a-z]{1,2})\. ([0-9])", new).group(2)
		new = new.replace(numlet + ". " + num, numlet + "." + num)	
	new = new.replace("  ", " ")
	new = new.replace("Li 5530 (", "Li 5530 Slg. Hardt (*, ")	
	new = insertPoint(new)
	new = adjustMus(new)
	return(new)
def adjustMus(sm):
	if "Mus" not in sm:
		return(sm)
	sm = sm.replace("Mus.", "Musica ")
	sm = sm.replace(" div", " div.")
	sm = sm.replace(" coll.inc.", " coll. inc.")
	sm = sm.replace(" Coll.Inc.", " coll. inc.")
	sm = sm.replace("fol.", " 2°")
	sm = sm.replace("H: ", "")
	sm = sm.replace("  ", " ")
	sm = sm.replace("..", ".")
	sm = sm.strip()
	return(sm)
def insertPoint(sm):
	stops = ["Schulenburg", "Kapsel"]
	for stop in stops:
		if stop in sm:
			return(sm)
	try:
		word = re.search(r"[A-Z][a-z]{2,}", sm).group(0)
	except:
		return(sm)
	else:
		sm = sm.replace(word, word + ".")
		sm = sm.replace("..", ".")
		return(sm)
def searchable(sm):
	sm = sm.replace("(", "\(")
	sm = sm.replace(")", "\)")
	return(sm)		