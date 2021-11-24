#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Dataset:
	def __init__(self):
		self.fields = {}
	def addEntry(self, field, entry):
		try:
			self.fields[field].append(entry)
		except:
			print("Feld " +  field + " ist nicht definiert")
	def getEntries(self, field):
		try:
			return(self.fields[field])
		except:
			return(None)
	def toDict(self):
		ret = {}
		for name in self.fields:
			ret[name] = ";".join([str(entry) for entry in self.fields[name]])
		return(ret)
	def toList(self):
		ret = []
		for name in self.fields:
			for entry in self.fields[name]:
				ret.append({name : str(entry)})
		return(ret)


class Entry:
	def __init__(self, value, lang = None, authSys = "", authID = ""):
		self.value = value
		self.language = lang
		self.authSys = authSys
		self.authID = authID
	def __str__(self):
		ret = self.value
		if self.language != None:
			ret = ret + "@" + self.language
		if self.authSys and self.authID:
			ret = ret + "#" + self.authSys + "_" + self.authID
		return(ret)

class DatasetDC(Dataset):
	def __init__(self):
		super().__init__()
		self.fields = {
			"identifier" : [],
			"format" : [],
			"type" : [],
			"language" : [],
			"title" : [],
			"subject" : [],
			"coverage" : [],
			"description" : [],
			"creator" : [],
			"contributor" : [],
			"publisher" : [],
			"rights" : [],
			"source" : [],
			"relation" : [],
			"date" : []
		}