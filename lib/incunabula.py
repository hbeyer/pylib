#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re

class Volume:
	def __init__(self, collection, core, content = []):
		self.collection = collection
		self.core = core
		self.content = content
	def __str__(self):
		ret = self.collection + ': ' + self.core
		for inc in self.content:
			ret += '\n\t ' + inc.shelfmark.part + ' ' + str(inc)
		return(ret)
	def addIncunabulum(self, incunabulum):
		if incunabulum.shelfmark.core == self.core and incunabulum.shelfmark.part:
			self.content.append(incunabulum)
	def countParts(self):
		return(len(self.content))
	def sortContent(self):
		self.content.sort(sortIncPart)

class Incunabulum:
	def __init__(self, ppn, epn, bbg, title, shelfmark, year):
		self.ppn = ppn
		self.epn = epn
		self.bbg = bbg
		self.title = title
		self.shelfmark = shelfmark
		self.year = year
		self.toDigitize = None
	def __str__(self):
		ret = abbr(self.title, 140) + ', ' + self.year + '; PPN ' + self.ppn
#		ret = self.title + ', ' + self.year + '; PPN ' + self.ppn
		if self.toDigitize == True:
			ret = ret + ' (zu digitalisieren)'
		return(ret)

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

def sortYear(a, b):
	if a['Jahr'] > b['Jahr']:
		return(1)
	if b['Jahr'] > a['Jahr']:
		return(-1)
	return(0)

def sortIncPart(a, b):
	if a.shelfmark.part == '':
		a.shelfmark.part = '0'
	if b.shelfmark.part == '':
		b.shelfmark.part = '0'
	if int(a.shelfmark.part) > int(b.shelfmark.part):
		return(1)
	if int(b.shelfmark.part) > int(a.shelfmark.part):
		return(-1)
	return(0)

def abbr(string, length):
	if len(string) > length:
		return(string[0:length] + '...')
	return(string)

def convertPart(string):
	if string == '':
		return(0)
	return(int(string))        