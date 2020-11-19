#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
from lib import localsql as ls

# Verarbeitung von CSV-Tabellen, die in der WinIBW generiert und unter path abgelegt wurden
class Table():
	def __init__(self, path):
		try:
			file = open(path, "r", encoding="cp1252")
		except:
			print("Keine Datei unter " + path)
			return(None)
		reader = csv.DictReader(file, delimiter=";")
		self.content = [row for row in reader]
		self.fields = [tup for tup in self.content[0] if tup != ""]
	def getByField(self, field):
		ret = [row[field] for row in self.content]
		return(ret)
	def getSelection(self, fields):
		ret = [[row[field] for field in fields] for row in self.content]
		return(ret)
	def filter(self, function = lambda row : row):
		self.content = [function(row) for row in self.content]
		# Gibt die function None aus, wird die entsprechende Zeile entfernt
		self.content = [row for row in self.content if row != None]
		return(self.content)
	def toSQLite(self, fileName = "exportTable"):
		db = ls.Database(self.fields, [[row[field] for field in self.fields] for row in self.content], fileName)
		return(True)
