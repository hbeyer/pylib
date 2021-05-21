#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv

class Table:
	def __init__(self, fields = [], content = []):
		self.content = content
		self.fields = fields
	def save(self, fileName):
		with open(fileName + ".csv", 'w', encoding="utf-8", newline="") as csvfile:
			writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			writer.writerow(self.fields)
			for row in self.content:
				writer.writerow(row)
	def load(self, path):
		try:
			file = open(path + ".csv", "r")
		except:
			print("Keine Datei unter " + path)
			return(None)
		reader = csv.reader(file, delimiter=";")
		self.content = [row for row in reader]
		self.fields = self.content.pop(0)