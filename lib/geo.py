#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ul
import xml.etree.ElementTree as et
import re
from lib import csvt

class GeoDB:
	def __init__(self, path = "placeData"):
		self.path = path
		self.table = csvt.Table([], [])
		self.table.load(self.path.replace(".csv", ""))
		self.index = {}
		count = 0
		for row in self.table.content:
			try:
				self.index[row[0]].append[count]
			except:
				self.index[row[0]] = [count]
			else:
				print("Dublette: " + row[0])
			count += 1
	def getByName(self, name):
		try:
			row = self.table.content[self.index[name][0]]
		except:
			return(False)
		else:
			return(row)
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
	def getGeoData(self):
		for row in self.table.content:
			if row[1] != "":
				gd = getGeoDataGetty(row[1])
			elif row[2] != "":
				gd = getGeoDataGND(row[2])
			if gd != False:
				row[3] = gd[0]
				row[4] = gd[1]
			else:
				print(row[0] + " - " + row[1])
				continue
def normalizePlaceName(placeName):
	placeName = re.sub(r"!\d+!", "", str(placeName))
	placeName = placeName.replace("?", "")
	placeName = placeName.strip()
	placeName = placeName.replace("$g", ", ")
	placeName = placeName.replace("[]", "")
	placeName = placeName.replace("()", "")
	placeName = placeName.strip()
	placeName = placeName.strip("@[]$,+!")
	conc = { 
		"Altenburg, Thüringen" : "Altenburg", 
		"Altdorf <bei Nürnberg>" : "Altdorf", 
		"Altdorf b. Nürnberg" : "Altdorf", 
		"Brandenburg <Havel>" : "Brandenburg", 
		"Clausthal-Zellerfeld" : "Clausthal", 
		"Dillingen a.d. Donau" : "Dillingen", 
		"Landkreis Dillingen a.d. Donau" : "Dillingen", 
		"Frankfurt" : "Frankfurt am Main", 
		"Frankfurt, Main" : "Frankfurt am Main", 
		"Frankfurt/M." : "Frankfurt am Main",
		"Frankfurt/Main" : "Frankfurt am Main", 			
		"Frankfurt <Main>" : "Frankfurt am Main", 			
		"Frankfurt a.M." : "Frankfurt am Main", 			
		"Frankfurt a. M." : "Frankfurt am Main", 			
		"Frankfurt [, Main]" : "Frankfurt am Main", 			
		"Frankfurt an der Oder" : "Frankfurt (Oder)", 
		"Frankfurt <Oder>" : "Frankfurt (Oder)", 
		"Frankfurt, Oder" : "Frankfurt (Oder)", 
		"Frankfurt a. d. Oder" : "Frankfurt (Oder)", 
		"Frankfurt a.d. Oder" : "Frankfurt (Oder)", 
		"Frankfurt/O." : "Frankfurt (Oder)", 
		"Frankfurt/Oder" : "Frankfurt (Oder)", 
		"Frankfurt <Oder>" : "Frankfurt (Oder)", 
		"Frankfurt (Oder) ; ID: gnd/4018122-4" : "Frankfurt (Oder)",
		"Frankfurt, main" : "Frankfurt am Main",
		"frankfurt, Main" : "Frankfurt am Main",
		"Frankfurt, Main," : "Frankfurt am Main",
		"Frankfurt, oder" : "Frankfurt am Main",
		"Frankfurt. Main" : "Frankfurt am Main",
		"Frankfurt/ Main" : "Frankfurt am Main",
		"Frankfurt; Oder" : "Frankfurt (Oder)",
		"Freiburg im Breisgau ; ID: gnd/4018272-1" : "Freiburg im Breisgau",
		"Freiburg, Breisgau" : "Freiburg im Breisgau",
		"Freiburg" : "Freiburg im Breisgau",
		"Freiburg i. Br." : "Freiburg im Breisgau",		
		"Giessae" : "Gießen",
		"Giessen" : "Gießen",
		"Gioeßen" : "Gießen",
		"Lutherstadt Wittenberg" : "Wittenberg", 
		"Halle, Saale" : "Halle (Saale)", 
		"Halle/S." : "Halle (Saale)", 
		"Halle/Saale" : "Halle (Saale)",
		"Halle" : "Halle (Saale)",
		"Halle Saale" : "Halle (Saale)",
		"Halle, Sachsen" : "Halle (Saale)",
		"Halle. Saale" : "Halle (Saale)",
		"Halle/ Saale" : "Halle (Saale)",
		"Hamm, Westfalen" : "Hamm",
		"Herborn, Lahn-Dill-Kreis" : "Herborn",
		"Hof (Saale)" : "Hof",
		"Hof / Saale" : "Hof",
		"Hof <Oberfranken>" : "Hof",
		"J" : "Jena",
		"Jauer" : "Jena",
		"Jehna" : "Jena",
		"Jenae" : "Jena",
		"KÖln" : "Köln",
		"Köngisberg" : "Königsberg",
		"Königsberg, Preussen" : "Königsberg",
		"Königsberga" : "Königsberg",
		"Königsgberg" : "Königsberg",
		"Kempten (Allgäu)" : "Kempten", 
		"Koppenhagen" : "Kopenhagen", 
		"Köthen (Anhalt)" : "Köthen", 
		"Lauingen (Donau)" : "Lauingen",
		"Lauingen, Donau" : "Lauingen",		
		"Leipzig; Frankfurt, Main" : "Leipzig",		
		"Lipsiae" : "Leipzig",		
		"Lignitz" : "Liegnitz",
		"Lissa <Posen>" : "Lissa",
		"Lindau, Bodensee" : "Lindau (Bodensee)",
		"Madgeburg" : "Magdeburg",
		"Magdaeburg" : "Magdeburg",
		"Mageburg" : "Magdeburg",
		"Magedeburg" : "Magdeburg",
		"Marburg/Lahn" : "Marburg",
		"Marpurg" : "Marburg",
		"Marpurgi" : "Marburg",
		"Meissen" : "Meißen",
		"Minden (Westf)" : "Minden",
		"Minden, Westfalen" : "Minden",
		"Mühlhausen/Thüringen" : "Mühlhausen",
		"Münster (Westf)" : "Münster",
		"Münster, Westfalen" : "Münster",
		"Naumburg (Saale)" : "Naumburg",
		"Neisse" : "Neiße",
		"Neuburg, Donau" : "Neuburg",
		"Neuheus" : "Neuhaus",
		"Newhaus" : "Neuhaus",
		"Newhauß" : "Neuhaus",
		"Neustadt a. d. Aisch" : "Neustadt an der Aisch",
		"Neustadt, Aisch" : "Neustadt an der Aisch",
		"Neustadt, Weinstraße" : "Neustadt an der Weinstraße",
		"Nürnebrg" : "Nürnberg",
		"Obermarchthal" : "Obermarchtal",
		"Oberursel (Taunus)" : "Oberursel",
		"Oettingen i. Bay." : "Oettingen",
		"Öttingen" : "Oettingen",
		"Offenbach am Main" : "Offenbach",
		"Rawitsch" : "Rawicz",
		"Regenburg" : "Regensburg",
		"Regenspurg" : "Regensburg",
		"Rostochii" : "Rostock",
		"Rothenburg <Tauber>" : "Rothenburg ob der Tauber",
		"Rothenburg" : "Rothenburg ob der Tauber",
		"Stargard" : "Stargard in Pommern",
		"Stargard Szczeciński" : "Stargard in Pommern",
		"Saalfeld/Saale" : "Saalfeld",
		"Schneeberg, Erzgebirgskrei" : "Schneeberg",
		"Stargard in Pommern" : "Stargard",
		"Statthagen" : "Stadthagen",
		"Steinau" : "Steinau an der Oder",
		"Steinau, Oder" : "Steinau an der Oder",
		"Stetin" : "Stettin",
		"Strasbourg" : "Straßburg",
		"Strassburg" : "Straßburg",
		"Sulzbach, Oberpfalz" : "Sulzbach",
		"Toruń" : "Thorn",
		"Wallstadt [i.e. Frankfurt, Main ]" : "Frankfurt am Main",
		"Weissenfels" : "Weißenfels",
		"Weißenfels <Halle, Saale>" : "Weißenfels",
		"Wilna" : "Vilnius",
		"wittenberg" : "Wittenberg",
		"Wittenberg4033 Wittenberg" : "Wittenberg",
		"Wittenbergae" : "Wittenberg",
		"Wolffenbüttel" : "Wolfenbüttel",
		"Wollgast" : "Wolgast",
		"Zerbst/Anhalt" : "Zerbst",
		"Zugl.: Frankfurt <Oder>" : "Frankfurt (Oder)",
		"Züllichow" : "Züllichau",
		"öln" : "Köln",
		}
	try:
		placeName = conc[placeName]
	except:
		pass
	return(placeName)
def getGeoDataGetty(id):
	url = "https://ref.de.dariah.eu/tgnsearch/tgnquery.xql?id=" + id
	fileobject = ul.urlopen(url, None, 10)
	tree = et.parse(fileobject)
	root = tree.getroot()
	latNode = root.find('.//{http://textgrid.info/namespaces/vocabularies/tgn}Latitude/{http://textgrid.info/namespaces/vocabularies/tgn}Decimal')
	longNode = root.find('.//{http://textgrid.info/namespaces/vocabularies/tgn}Longitude/{http://textgrid.info/namespaces/vocabularies/tgn}Decimal')
	try:
		latitude = latNode.text.strip()
	except:
		return(False)
	else:
		try:
			longitude = longNode.text.strip()
		except:
			return(False)
		else:
			return([longitude, latitude])
def getGeoDataGND(id):
	url = "http://d-nb.info/gnd/" + id + "/about/lds"
	fileobject = ul.urlopen(url, None, 10)
	text = fileobject.read()
	snippet = re.search(r"Point \( ([\+\-]\d+\.\d+) ([\+\-]\d+\.\d+) \)", str(text))
	try:
		longitude = snippet.group(1)
	except:
		return(False)
	else:
		try:
			latitude = snippet.group(2)
		except:
			return(False)
		return(longitude, latitude)