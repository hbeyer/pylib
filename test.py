#!/usr/bin/python3
# -*- coding: utf-8 -*-


import csv
from lib import csvt
from lib import geo

"""
conc = {
	"Staatliche Bibliothek Ansbach (Sigel: 127)" : { "place" : "Ansbach", "bib" : "Staatliche Bibliothek" },
	"Provinzialbibliothek Amberg (Sigel: 54)" : { "place" : "Amberg", "bib" : "Provinzialbibliothek" },
	"Hofbibliothek Aschaffenburg (Sigel: 128)" : { "place" : "Aschaffenburg", "bib" : "Hofbibliothek" },
	"Universitätsbibliothek Augsburg (Sigel: 384)" : { "place" : "Augsburg", "bib" : "Universitätsbibliothek" },
	"Staats- und Stadtbibliothek Augsburg (Sigel: 37)" : { "place" : "Augsburg", "bib" : "Staats- und Stadtbibliothek" },	
	"Staatsbibliothek Bamberg (Sigel: 22)" : { "place" : "Bamberg", "bib" : "Staatsbibliothek" },	
	"Universitätsbibliothek Bayreuth (Sigel: 703)" : { "place" : "Bayreuth", "bib" : "Universitätsbibliothek" },	
	"Geheimes Staatsarchiv Preußischer Kulturbesitz, Bibliothek" : { "place" : "Berlin", "bib" : "Geheimes Staatsarchiv Preußischer Kulturbesitz" },	
	"Landesbibliothek Coburg (Sigel: 70)" : { "place" : "Coburg", "bib" : "Landesbibliothek" },
	"Studienbibliothek Dillingen (Sigel: Di 1)" : { "place" : "Dillingen", "bib" : "Studienbibliothek" },
	"Universitätsbibliothek Eichstätt - Zentralbibliothek und Teilbibliotheken in Eichstätt (Sigel: 824)" : { "place" : "Eichstätt", "bib" : "Universitätsbibliothek" },
	"Universitätsbibliothek Erlangen-Nürnberg, Hauptbibliothek (Sigel: 29)" : { "place" : "Erlangen", "bib" : "Universitätsbibliothek Erlangen-Nürnberg" },
	"Landeskirchliches Archiv der Evangelisch-Lutherischen Kirche in Bayern (Sigel: N 26)" : { "place" : "Nürnberg", "bib" : "Landeskirchliches Archiv der Evangelisch-Lutherischen Kirche in Bayern" },
	"Bayerische Staatsbibliothek München (Sigel: 12)" : { "place" : "München", "bib" : "Bayerische Staatsbibliothek" },
	"Deutsches Museum München (Sigel: 210)" : { "place" : "München", "bib" : "Deutsches Museum" },
	"Bibliothek der Ludwig-Maximilians-Universität München (Sigel: 19)" : { "place" : "München", "bib" : "Universitätsbibliothek" },
	"Staatliche Bibliothek Neuburg an der Donau (Sigel: 150)" : { "place" : "Neuburg an der Donau", "bib" : "Staatliche Bibliothek" },
	"Alte Bibliothek der Abtei Ottobeuren" : { "place" : "Ottobeuren", "bib" : "Alte Bibliothek der Abtei Ottobeuren" },
	"Staatsbibliothek Passau (Sigel: 154)" : { "place" : "Passau", "bib" : "Staatsbibliothek" },
	"Staatliche Bibliothek Regensburg (Sigel: 155)" : { "place" : "Regensburg", "bib" : "Staatliche Bibliothek" },
	"Universitätsbibliothek Regensburg (Sigel: 355)" : { "place" : "Regensburg", "bib" : "Universitätsbibliothek" },
	"Hofbibliothek Thurn und Taxis Regensburg (Sigel: 76)" : { "place" : "Regensburg", "bib" : "Hofbibliothek Thurn und Taxis" },
	"Universitätsbibliothek Würzburg (Sigel: 20)" : { "place" : "Würzburg", "bib" : "Universitätsbibliothek" }
}

res = csvt.Table(["VDN", "Ort", "Bibliothek", "Signatur"], [])
path = "/home/hbeyer/Downloads/bvb65"
file = open(path + ".csv", "r")
reader = csv.reader(file, delimiter=";")
for row in reader:
	vdn = row[0]
	if row[1] == "13":
		print(row)
	if row[1] in conc:
		place = conc[row[1]]["place"]
		bib = conc[row[1]]["bib"]
	else:
		split = row[1].split(", ")
		try:
			place = split[0]
		except:
			place = "ohne"
		try:
			bib = split[1]
		except:
			bib = "ohne"
	sigList = [part for part in row[2:7] if part != ""]
	sig = ", ".join(sigList)
	new = [vdn, place, bib, sig]
	res.content.append(new)
res.save("Exemplare_VD16")
"""


db = geo.DB()
res = {}
table = csvt.Table([], [])
table.load("Exemplare_VD16")
for row in table.content:
	bibID = row[1] + row[2][0:5]
	try:
		res[bibID]["count"] += 1
	except:
		res[bibID] = { "place" : row[1], "bib" : row[2], "count" : 1 }
newTable = csvt.Table(["ID", "Ort", "Bibliothek", "Anzahl_Exemplare", "longitude", "latitude"], [])
for key in res:
	longitude = ""
	latitude = ""
	pd = db.getByName(res[key]["place"])
	try:
		longitude = pd[3]
	except:
		pass
	else:
		try:
			latitude = pd[4]
		except:
			pass
	newTable.content.append([key, res[key]["place"], res[key]["bib"], res[key]["count"], longitude, latitude])
newTable.save("Kartierung_VD16")