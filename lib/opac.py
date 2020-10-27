#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ur
import re
import urllib.parse as up
import os.path as op
import xml.etree.ElementTree as et


class grabber:
	def __init__(self, query):
		self.query = query
		self.url = "http://opac.lbs-braunschweig.gbv.de/DB=2/XML=1.0/CMD?ACT=SRCHA&TRM=" + up.quote(self.query)
		fileobject = ur.urlopen(self.url)
		self.response = ""
		self.numFound = None
		try:
			self.response = fileobject.read().decode('utf-8')
		except:
			print("Keine Antwort von " + self.url)
		else:
			test = re.search(r"hits=\"([0-9]+)\"", self.response)
			try:
				self.numFound = test.group(1)
			except:
				print("Keine Antwort bei " + self.url)
				self.numFound = 0