#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

class Shelfmark:
	def __init__(self, whole):
		self.whole = whole.strip()
		self.collection = ''
		self.core = ''
		self.part = ''
		self.valid = 0
		extract = re.search(r"(A|H|M|Bibel-S\.|Ältere Einblattdrucke|aeltere einblattdrucke|S: Alv\.|Cod\. Guelf\.):? ([^\(]+)", self.whole)
		if extract != None:
			if extract.group(1):
				self.collection = extract.group(1).strip()
			if extract.group(2):
				self.core = extract.group(2).strip()
		extract = re.search(r"\(([0-9]{1,2})\)", self.whole)
		if extract != None:
			if extract.group(1):
				self.part = extract.group(1)
		if self.collection and self.core:
			self.valid = 1
	def __str__(self):
		ret = self.collection + ': ' + self.core
		if self.part:
			ret += ' (' + self.part + ')'
		return(ret)
def convertOld(old):
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