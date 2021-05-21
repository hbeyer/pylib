#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ul
import xml.etree.ElementTree as et
import re
from lib import csvt

class GeoDB:
	def __init__(self, path):
		self.path = path
		self.table = csvt.Table([], [])
		self.table.load(self.path.replace(".csv", ""))
	def save(self):
		self.table.save(self.path.replace(".csv", ""))
	def addPlace(self, placeName, getty = "", gnd = "", long = "", lat = ""):
		placeName = self.normalizePlaceName(placeName)
		for row in self.table.content:
			if placeName == row[0]:
				return(False)
			if getty != "" and getty == row[1]:
				return(False)
			if gnd != "" and gnd == row[2]:
				return(False)
		new = [placeName, getty, gnd, long, lat]
		self.table.content.append(new)
		return(True)
	def normalizePlaceName(self, placeName):
		placeName = re.sub(r"!\d+!", "", str(placeName))
		conc = { 
			"Frankfurt, Main" : "Frankfurt am Main", 
			"Frankfurt an der Oder" : "Frankfurt (Oder)", 
			"Frankfurt/M." : "Frankfurt am Main", 
			"Frankfurt/Main" : "Frankfurt am Main", 
			"Lutherstadt Wittenberg" : "Wittenberg", 
			"Halle/S." : "Halle (Saale)", 
			"Halle/Saale" : "Halle (Saale)", 
			"Freiburg i. Br." : "Freiburg im Breisgau" }
		try:
			placeName = conc[placeName]
		except:
			pass
		return(placeName)