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
		try:
			self.ppn = self.getValues("003@", "0").pop(0)
		except:
			self.ppn = ""
		try:			
			self.bbg = self.getValues("002@", "0").pop(0)
		except:
			self.bbg = ""
		self.vdn = self.getValues("006V", "0")
		try:
			self.title = self.getValues("021A", "a").pop(0)
		except:
			self.title = ""
		self.altTitles = self.getValues("027a", "a")
		self.vd16m = self.getValues("006L", "0")
		try:
			self.date = self.getValues("011@", "a").pop(0)
		except:
			self.date = ""
		self.shelfmarks = self.getValues("209A", "a")
	def __str__(self):
		ret = "record: PPN " + self.ppn + ", VDN: " + "|".join(self.vdn) + ", Jahr: " + self.date
		return(ret)
	def getValues(self, field, subfield):
		fields = self.node.findall(".//{info:srw/schema/5/picaXML-v1.0}datafield[@tag='" + field + "']/{info:srw/schema/5/picaXML-v1.0}subfield[@code='" + subfield + "']")
		if fields:
			return([field.text for field in fields])
		return([])