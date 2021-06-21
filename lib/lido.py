#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ul
import xml.etree.ElementTree as et

class Record:
	def __init__(self, node):
		self.ns = { "lido" : "{http://www.lido-schema.org}" }
		self.node = node
		self.persons = []
		try:
			self.idRec = self.getFieldValues("lidoRecID").pop(0)
		except:
			self.idRec = ""
			print("Leere ID")
		try:
			self.id = self.idRec.split(":").pop(-1)
		except:
			self.id = ""
			print("ID nicht lesbar: " + self.idRec)
		try:
			self.title = ", ".join(self.getPathValues(".//" + self.ns["lido"] + "titleSet/" + self.ns["lido"] + "appellationValue"))
		except:
			self.title = ""
			print("Kein Titel (ID " + self.id + ")")
		self.technique = self.getPathValues(".//" + self.ns["lido"] + "termMaterialsTech/" + self.ns["lido"] + "term")
		self.getPersons()
		self.getLinks()
	def getPersons(self):
		evnn = self.node.findall(".//" + self.ns["lido"] + "event")
		for en in evnn:
			try:
				evType = en.findall(".//" + self.ns["lido"] + "eventType/" + self.ns["lido"] + "term")[0]
			except:
				continue
			if evType.text == "Erschaffung/Herstellung":
				eaa = en.findall(".//" + self.ns["lido"] + "eventActor")
				for ea in eaa:
					try:
						name = ea.findall(".//" + self.ns["lido"] + "appellationValue")[0].text
					except:
						name = "?"
					pers = Person(name)
					try:
						pers.role = ea.findall(".//" + self.ns["lido"] + "roleActor/" + self.ns["lido"] +  "term")[0].text
					except:
						pass
					self.persons.append(pers)
	def getLinks(self):
		repp = self.node.findall(".//" + self.ns["lido"] + "resourceRepresentation")
		for rp in repp:
			rty = rp.get(self.ns["lido"] + "type")
			try:
				link = rp.findall(".//" + self.ns["lido"] + "linkResource")[0].text
			except:
				continue
			if rty == "display":
				self.image = link
			elif rty == "thumbnail":
				self.thumb = link
			elif rty == "purl":
				self.purl = link					
	def getFieldValues(self, field):
		ret = []
		ndd = self.node.findall(".//" + self.ns["lido"] + field)
		for nd in ndd:
			ret.append(nd.text)
		return(ret)
	def getPathValues(self, path):
		ret = []
		ndd = self.node.findall(path)
		for nd in ndd:
			ret.append(nd.text)
		return(ret)
class Person():
	def __init__(self, persName):
		self.persName = persName
		self.role = ""
	def __str__(self):
		ret = self.persName
		if self.role != "":
			ret = ret + " (" + self.role + ")"
		return(ret)