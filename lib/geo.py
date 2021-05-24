#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ul
import xml.etree.ElementTree as et
import re
from lib import csvt

class DB:
	def __init__(self, path = "placeData"):
		self.path = path
		self.table = csvt.Table([], [])
		self.table.load(self.path.replace(".csv", ""))
		self.index = {}
		self.makeIndex()
	def makeIndex(self):
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
		self.table.content.sort(key=lambda row: row[0])
		self.table.save(self.path.replace(".csv", ""))
	def addPlace(self, placeName, getty = "", gnd = "", long = "", lat = ""):
		placeName = normalizePlaceName(placeName)
		for row in self.table.content:
			if placeName == row[0]:
				return(False)
			if getty != "" and getty == row[1]:
				return(False)
			if gnd != "" and gnd == row[2]:
				return(False)
		new = [placeName, getty, gnd, long, lat]
		self.table.content.append(new)
		self.makeIndex()
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
	placeName = re.sub(r"![0-9Xx]!", "", str(placeName))
	placeName = placeName.replace("?", "")
	placeName = placeName.strip()
	placeName = placeName.replace("$g", ", ")
	placeName = placeName.replace("[]", "")
	placeName = placeName.replace("()", "")
	placeName = placeName.strip()
	placeName = placeName.strip("@[]$,+!")
	conc = { 
		"00696074X" : "", 
		"|bema|*ad*Digitalisierung UB Leipzig$2014-2016" : "", 
		"Normierter Ort" : "", 
		"S.l." : "s.l.", 
		"Fingiert" : "fingiert", 
		"Altenburg, Thüringen" : "Altenburg", 
		"ALtenburg" : "Altenburg", 
		"Altenburgi" : "Altenburg", 
		"Altdorf <bei Nürnberg>" : "Altdorf", 
		"Altdorf b. Nürnberg" : "Altdorf", 
		"altdorf" : "Altdorf", 
		"Altorf" : "Altdorf", # Vielleicht auch Altorf im Elsass
		"Aldorf" : "Altdorf", # Vielleicht auch Altorf im Elsass
		"Altendorf" : "Altdorf",
		"Alten Stettin" : "Stettin",
		"Baden" : "Baden (Aargau)", 
		"Bernburg (Saale)" : "Bernburg", 
		"Beyreuth" : "Bayreuth", 
		"Blankenburg (Harz)" : "Blankenburg", 
		"Brandenburg <Havel>" : "Brandenburg", 
		"Breisach" : "Breisach am Rhein",
		"Bruntraut" : "Pruntrut",
		"Burgdorf" : "Basel", # Fehler im VD17
		"Annaberg <Erzgebirge>" : "Annaberg-Buchholz", 
		"Annaberg" : "Annaberg-Buchholz", 
		"Augspurg" : "Augsburg", 
		"Clausthal-Zellerfeld" : "Clausthal", 
		"Dillingen a.d. Donau" : "Dillingen", 
		"Dillingen a. d. Donau" : "Dillingen", 
		"Dortmundt" : "Dortmund", 
		"Dreßden" : "Dresden", 
		"Dyhernfurth" : "Dyhernfurt", 
		"Eichstädt" : "Eichstätt", 
		"Eisenberg (Saale-Holzland-Kreis)" : "Eisenberg", 
		"Enckhüsen" : "Enkhuizen", 
		"Esslingen am Neckar" : "Esslingen", 
		"Eßlingen" : "Esslingen", 
		"Embden" : "Emden", 
		"Emmerich am Rhein" : "Emmerich", 
		"Erurt" : "Erfurt", 
		"ERfurt" : "Erfurt", 
		"Erffurt" : "Erfurt", 
		"Landkreis Dillingen a.d. Donau" : "Dillingen",
		"Forchheim (Oberfr.)" : "Forchheim",
		"Frankenthal (Pfalz)" : "Frankenthal",
		"Frankfurt" : "Frankfurt am Main", 
		"Frankfurt, Main" : "Frankfurt am Main", 
		"Frankfurt/M." : "Frankfurt am Main",
		"Frankfurt/Main" : "Frankfurt am Main", 			
		"Frankfurt <Main>" : "Frankfurt am Main", 			
		"Frankfurt a.M." : "Frankfurt am Main", 			
		"Frankfurt a. M." : "Frankfurt am Main", 			
		"Frankfurt [, Main]" : "Frankfurt am Main", 			
		"Francofurti ad Moenum" : "Frankfurt am Main", 			
		"Franckfurt am Mayn" : "Frankfurt am Main", 			
		"Francfurt, Main" : "Frankfurt am Main", 			
		"Frankfurt , Main" : "Frankfurt am Main", 			
		"Frankfurt an der Oder" : "Frankfurt (Oder)", 
		"Frankfurt <Oder>" : "Frankfurt (Oder)", 
		"Frankfurt, Oder" : "Frankfurt (Oder)", 
		"Frankfurt a. d. Oder" : "Frankfurt (Oder)", 
		"Frankfurt a.d. Oder" : "Frankfurt (Oder)", 
		"Frankfurt/O." : "Frankfurt (Oder)", 
		"Frankfurt/Oder" : "Frankfurt (Oder)", 
		"Frankfurt <Oder>" : "Frankfurt (Oder)", 
		"Frankfurt (Oder) ; ID: gnd/4018122-4" : "Frankfurt (Oder)",
		"104757892!Frankfurt (Oder)" : "Frankfurt (Oder)",
		"Frankfurt, main" : "Frankfurt am Main",
		"frankfurt, Main" : "Frankfurt am Main",
		"Frankfurt, Main," : "Frankfurt am Main",
		"Frankfurt, oder" : "Frankfurt am Main",
		"Frankfurt. Main" : "Frankfurt am Main",
		"Frankfurt/ Main" : "Frankfurt am Main",
		"Frankfurt [, Main" : "Frankfurt am Main",
		"Frankfurt; Oder" : "Frankfurt (Oder)",
		"Freiburg im Breisgau ; ID: gnd/4018272-1" : "Freiburg im Breisgau",
		"Freiburg, Breisgau" : "Freiburg im Breisgau",
		"Freiburg" : "Freiburg im Breisgau",
		"Freiburg i. Br." : "Freiburg im Breisgau",		
		"FReiberg" : "Freiberg",		
		"Freystadt, Schlesien" : "Freystadt in Schlesien",		
		"Freystadt, Niederschlesien" : "Freystadt in Schlesien",		
		"Freystadt (Niederschlesien)" : "Freystadt in Schlesien",		
		"Friedberg" : "Friedberg (Hessen)",		
		"Friedland" : "Friedland (Mecklenburg)",		
		"Friedland (Landkreis Mecklenburgische Seenplatte)" : "Friedland (Mecklenburg)",		
		"Giessae" : "Gießen",
		"Giessen" : "Gießen",
		"Gioeßen" : "Gießen",
		"Geifswald" : "Greifswald",
		"Gothag" : "Gotha",
		"Grossenhain" : "Großenhain",
		"Grönau" : "Groß Grönau",
		"Gubin" : "Guben",
		"Helmstädt" : "Helmstedt",
		"Helmstedtt" : "Helmstedt",
		"Lutherstadt Wittenberg" : "Wittenberg", 
		"Hagen" : "Altdorf", # Fehler im VD17 (Drucker: Georg Hagen)
		"Halberstedt" : "Halberstadt", 
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
		"Hirschberg im Riesengebirge" : "Hirschberg",
		"Hof (Saale)" : "Hof",
		"Hof / Saale" : "Hof",
		"Hof <Oberfranken>" : "Hof",
		"Höchstädt a. d. Donau" : "Höchstädt an der Donau",
		"Kaisersheim" : "Kaisheim",
		"J" : "Jena",
		"Jauer" : "Jena",
		"Jehna" : "Jena",
		"Jenae" : "Jena",
		"Iena" : "Jena",
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
		"Landsberg" : "Landsberg am Lech",		
		"Leipzig; Frankfurt, Main" : "Leipzig",		
		"leipzig" : "Leipzig",		
		"Lipsiae" : "Leipzig",		
		"Lignitz" : "Liegnitz",
		"Lissa <Posen>" : "Lissa",
		"Lindau, Bodensee" : "Lindau (Bodensee)",
		"Löwenburg, Schweiz" : "Löwenburg JU",
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
		"Neustadt, Saale" : "Neustadt an der Saale",
		"Bad Neustadt an der Saale" : "Neustadt an der Saale",
		"Nürnebrg" : "Nürnberg",
		"Obermarchthal" : "Obermarchtal",
		"Oberursel (Taunus)" : "Oberursel",
		"Oettingen i. Bay." : "Oettingen",
		"Öttingen" : "Oettingen",
		"Offenbach am Main" : "Offenbach",
		"Prag." : "Prag",
		"Rawitsch" : "Rawicz",
		"Regenburg" : "Regensburg",
		"Regenspurg" : "Regensburg",
		"Rostochii" : "Rostock",
		"Rothenburg <Tauber>" : "Rothenburg ob der Tauber",
		"Rothenburg" : "Rothenburg ob der Tauber",
		"Rodolstadt" : "Rudolstadt",
		"Stargard" : "Stargard in Pommern",
		"Stargard Szczeciński" : "Stargard in Pommern",
		"Saalfeld/Saale" : "Saalfeld",
		"Schneeberg, Erzgebirgskreis" : "Schneeberg",
		"Stargard in Pommern" : "Stargard",
		"Statthagen" : "Stadthagen",
		"Steinau" : "Steinau an der Oder",
		"Steinau, Oder" : "Steinau an der Oder",
		"Stetin" : "Stettin",
		"Strasbourg" : "Straßburg",
		"Strassburg" : "Straßburg",
		"Argentorati" : "Straßburg",
		"Sulzbach, Oberpfalz" : "Sulzbach",
		"Toruń" : "Thorn",
		"Wallstadt [i.e. Frankfurt, Main " : "Frankfurt am Main",
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