#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv

# Verarbeitung von CSV-Tabellen, die in der WinIBW generiert und unter path abgelegt wurden
class Table():
	def __init__(self, path):
		try:
			file = open(path, "r", encoding="cp1252")
		except:
			print("Keine Datei unter " + path)
			return(None)
		self.reader = csv.DictReader(file, delimiter=";")
		self.content = [row for row in self.reader]
	def getFieldNames(self):
		self.fields = [tup for tup in self.content[0]]
		return(self.fields)
	def getByField(self, field):
		ret = [row[field] for row in self.content]
		return(ret)
	def getSelection(self, fields):
		ret = [[row[field] for field in fields] for row in self.content]
		return(ret)
	def filter(self, function = lambda row : row):
		self.content = [function(row) for row in self.content]
		self.content = [row for row in self.content if row != None]
		return(self.content)