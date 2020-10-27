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