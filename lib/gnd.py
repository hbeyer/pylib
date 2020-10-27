#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import urllib.request as ur

class id:
	valid = 0
	def __init__(self, gnd):
		self.gnd = str(gnd)[0:10]
		test = re.match('[0-9X-]{8,10}', self.gnd)
		if test != None:
			valid = 1

class request:
	base = 'http://hub.culturegraph.org/entityfacts/'
	def __init__(self, id):
		if id.valid == 1:
			url = self.base + id.gnd
			fileobject = ur.urlopen(url)
			string = fileobject.read()
			print(string)
		else:
			print('Ungültige ID übergeben')