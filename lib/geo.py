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
        self.make_index()
    def make_index(self):
        count = 0
        for row in self.table.content:
            try:
                self.index[row[0]].append[count]
            except:
                self.index[row[0]] = [count]
            else:
                print("Dublette: " + row[0])
            count += 1        
    def get_by_name(self, name):
        name = normalize_placename(name)
        try:
            row = self.table.content[self.index[name][0]]
        except:
            return(None)
        else:
            return(row)
    def get_dict(self, name):
        row = self.get_by_name(name)
        if row == None:
            return(None)
        return({"placeName" : row[0], "getty" : row[1], "gnd" : row[2], "long" : row[3], "lat" : row[4], "comment" : row[5]})
    def normalize_name(self, name):
        name = name.strip()
        row = self.get_by_name(name)
        if row == False:
            return(name)
        return(row[0])
    def get_coord(self, name):
        name = normalize_placename(name)
        try:
            row = self.table.content[self.index[name][0]]
        except:
            return(["", ""])
        return([row[3], row[4]])
    def save(self):
        self.table.content.sort(key=lambda row: row[0])
        self.table.save(self.path.replace(".csv", ""))
    def add_place(self, placeName, getty = "", gnd = "", long = "", lat = "", comment = ""):
        placeName = normalize_placename(placeName)
        for row in self.table.content:
            if placeName == row[0]:
                return(False)
            if getty != "" and getty == row[1]:
                return(False)
            if gnd != "" and gnd == row[2]:
                return(False)
        new = [placeName, getty, gnd, long, lat, comment]
        self.table.content.append(new)
        self.make_index()
        return(True)
    def get_geodata(self):
        for row in self.table.content:
            gd = False
            if row[3] == "":
                if row[1] != "":
                    gd = get_geodata_getty(row[1])
                elif row[2] != "":
                    gd = get_geodata_gnd(row[2])
                if gd != False:
                    row[3] = gd[0]
                    row[4] = gd[1]
                elif row[1] != "":
                    print(row[0] + " - http://vocab.getty.edu/page/tgn/" + row[1])
                elif row[2] != "":
                    print(row[0] + " - http://d-nb.info/gnd/4494563-2" + row[2])
                else:
                    print("Leer: " + row[0])
        return(True)
def normalize_placename(placeName):
    try:
        placeName = re.find(r"!.+!([^;]+) ; ID: gnd", str(placeName)).group(1)
    except:
        pass
    #placeName = re.sub(r"![0-9Xx]!", "", str(placeName))
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
        "Text lat." : "", 
        "Normierter Ort" : "", 
        "Normierter Ort neu" : "", 
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
        "Apenrade" : "Åbenrå",
        "Alten Stettin" : "Stettin",
        "Bad Frankenhausen" : "Frankenhausen", 
        "Bad Hersfeld" : "Hersfeld", 
        "Frankenhausen (Kyffhäuser)" : "Frankenhausen", 
        "Bad Frankenhausen (Kyffhäuser)" : "Frankenhausen", 
        "Bad Lobenstein" : "Lobenstein",
        "Baden" : "Baden (Aargau)", 
        "Bernburg (Saale)" : "Bernburg", 
        "Beyreuth" : "Bayreuth", 
        "Beuthen an der Oder" : "Bytom Odrzański",
        "Bingen am Rhein" : "Bingen", 
        "Blankenburg (Harz)" : "Blankenburg", 
        "Brandenburg <Havel>" : "Brandenburg", 
        "Braunsberg" : "Braniewo",
        "Braunsberg (Ostpreußen)" : "Braniewo",
        "Breisach" : "Breisach am Rhein",
        "Bruntraut" : "Pruntrut",
        "Brno" : "Brünn",
        "Burgdorf" : "Basel", # Fehler im VD17
        "Bruck" : "Klosterbruck",
        "Bruxelles" : "Brüssel", # Fehler im VD17
        "Bucuresti" : "Bukarest", # Fehler im VD17
        "Annaberg <Erzgebirge>" : "Annaberg-Buchholz", 
        "Annaberg" : "Annaberg-Buchholz", 
        "St. Annaberg" : "Annaberg-Buchholz", 
        "Augspurg" : "Augsburg", 
        "Cölln" : "Köln",
        "Cambridge/Massachusetts" : "Cambridge/Mass.", 
        "Clausthal-Zellerfeld" : "Clausthal", 
        "Dillingen a.d. Donau" : "Dillingen", 
        "Dillingen a. d. Donau" : "Dillingen", 
        "Dortmundt" : "Dortmund", 
        "Dreßden" : "Dresden", 
        "Dresden-Friedrichstadt" : "Dresden", 
        "Dyhernfurth" : "Dyhernfurt", 
        "Eichstädt" : "Eichstätt", 
        "Eisenberg (Saale-Holzland-Kreis)" : "Eisenberg", 
        "Ellwangen (Jagst)" : "Ellwangen",
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
        "Frankfurt/" : "Frankfurt am Main",
        "Frankfurt/Main" : "Frankfurt am Main",             
        "Frankfurt <Main>" : "Frankfurt am Main",             
        "Frankfurt a.M." : "Frankfurt am Main",             
        "Frankfurt a. M." : "Frankfurt am Main",             
        "Frankfurt [, Main]" : "Frankfurt am Main",             
        "Francofurti ad Moenum" : "Frankfurt am Main",             
        "Franckfurt am Mayn" : "Frankfurt am Main",             
        "Francfurt, Main" : "Frankfurt am Main",             
        "Frankfurt , Main" : "Frankfurt am Main",             
        "Frankfurt (Main)" : "Frankfurt am Main",             
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
        "Freiburg/Breisgau" : "Freiburg im Breisgau",
        "Freiburg/Br." : "Freiburg im Breisgau",
        "FReiberg" : "Freiberg",
        "Freiburg/Schweiz" : "Freiburg, Schweiz",
        "Freiburg im Üechtland" : "Freiburg, Schweiz",
        "Freiburg im Üechtland" : "Freiburg, Schweiz",
        "Freiburg in Schlesien" : "Świebodzice",
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
        "Gniezno (Gnesen)" : "Gnesen",
        "Gniezno" : "Gnesen",
        "Goerlitz" : "Görlitz",
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
        "Hamburgk" : "Hamburg",
        "Hamm, Westfalen" : "Hamm",
        "helmstedt" : "Helmstedt",
        "Herborn, Lahn-Dill-Kreis" : "Herborn",
        "Hirschberg im Riesengebirge" : "Hirschberg",
        "Hof (Saale)" : "Hof",
        "Hof / Saale" : "Hof",
        "Hof <Oberfranken>" : "Hof",
        "Höchstädt a. d. Donau" : "Höchstädt an der Donau",
        "Kaisersheim" : "Kaisheim",
        "Isny im Allgäu" : "Isny",
        "J" : "Jena",
        "Jauer" : "Jawor",
        "Jehna" : "Jena",
        "Jenae" : "Jena",
        "Jelgava" : "Mitau",
        "Iena" : "Jena",
        "KÖln" : "Köln",
        "Köngisberg" : "Königsberg",
        "Königsberg, Preussen" : "Königsberg",
        "Königsberga" : "Königsberg",
        "Königsgberg" : "Königsberg",
        "Kobenhavn" : "Kopenhagen",
        "Kempten (Allgäu)" : "Kempten", 
        "Koppenhagen" : "Kopenhagen", 
        "Köthen (Anhalt)" : "Köthen", 
        "Lauenburg" : "Lauenburg an der Elbe",
        "Lauingen (Donau)" : "Lauingen",
        "Lauingen, Donau" : "Lauingen",        
        "Lauffenburg" : "Laufenburg",        
        "Landsberg" : "Landsberg am Lech",        
        "Leipzig; Frankfurt, Main" : "Leipzig",        
        "leipzig" : "Leipzig",        
        "Leipzig." : "Leipzig",
        "Leitomischel" : "Litomyšl",
        "Leitomischl" : "Litomyšl",
        "Leutomischel" : "Litomyšl",    
        "Leuwarden" : "Leeuwarden",        
        "Lindau (Bodensee)" : "Lindau", 
        "Lindau, Bodensee" : "Lindau",          
        "Lingen (Ems)" : "Lingen",        
        "Lipsiae" : "Leipzig",        
        "Lignitz" : "Liegnitz",
        "Lissa <Posen>" : "Leszno",
        "Lissa" : "Leszno",
        "Lindau, Bodensee" : "Lindau (Bodensee)",
        "Lucern" : "Luzern",
        "Luxembourg" : "Luxemburg",
        "Louvain" : "Löwen",
        "Löwenburg, Schweiz" : "Löwenburg JU",
        "Lübben (Spreewald)" : "Lübben",
        "Madgeburg" : "Magdeburg",
        "Magdaeburg" : "Magdeburg",
        "Mageburg" : "Magdeburg",
        "Magedeburg" : "Magdeburg",
        "Magdebvrg" : "Madgeburg",
        "Marburg/Lahn" : "Marburg",
        "Marpurg" : "Marburg",
        "Marpurgi" : "Marburg",
        "Meissen" : "Meißen",
        "Minden (Westf)" : "Minden",
        "Minden, Westfalen" : "Minden",
        "Mintzel" : "Hof",
        "Mömpelgard" : "Montpellier",
        "Mühlhausen/Thüringen" : "Mühlhausen",
        "Mühlheim" : "Mülheim am Rhein",
        "Mülheim" : "Mülheim am Rhein",
        "Münster (Westf)" : "Münster",
        "Münster, Westfalen" : "Münster",
        "Münden" : "Hann. Münden",
        "Naumburg" : "Naumburg (Saale)",
        "Nehrling" : "",
        "Neisse" : "Neiße",
        "Neuburg, Donau" : "Neuburg",
        "Neuburg/Donau" : "Neuburg",
        "Neuburg a.d. Donau" : "Neuburg",
        "Neuheus" : "Neuhaus",
        "Newhaus" : "Neuhaus",
        "Newhauß" : "Neuhaus",
        "Neuhausen/Erzgeb." : "Neuhausen",
        "Neustadt a. d. Aisch" : "Neustadt an der Aisch",
        "Neustadt, Aisch" : "Neustadt an der Aisch",
        "Neustadt/Aisch" : "Neustadt an der Aisch",
        "Neustadt/Haardt" : "Neustadt an der Weinstraße",
        "Neustadt an der Haardt" : "Neustadt an der Weinstraße",
        "Neustadt, Orla" : "Neustadt an der Orla",
        "Neustadt, Weinstraße" : "Neustadt an der Weinstraße",
        "Neustadt, Saale" : "Neustadt an der Saale",
        "Nimwegen" : "Nijmegen",
        "Bad Neustadt an der Saale" : "Neustadt an der Saale",        
        "Norden (Landkreis Aurich)" : "Norden",
        "Nürnebrg" : "Nürnberg",
        "Obermarchthal" : "Obermarchtal",
        "Oberursel (Taunus)" : "Oberursel",
        "Oettingen i. Bay." : "Oettingen in Bayern",
        "Oettingen" : "Oettingen in Bayern",
        "Öttingen" : "Oettingen in Bayern",
        "Offenbach am Main" : "Offenbach",
        "Oldenburg (Oldenburg)" : "Oldenburg",
        "Opava" : "Troppau",
        "Osterode" : "Osterode am Harz",
        "Paderborn- Schloss Neuhaus" : "Schloss Neuhaus",
        "Philadelphia" : "fingiert",
        "Pirmont" : "Pyrmont",
        "Poznań" : "Posen",
        "Prag." : "Prag",
        "Prag-Neustadt" : "Prag",
        "Raudten" : "Rudna",
        "Rawitsch" : "Rawicz",
        "Regenburg" : "Regensburg",
        "Regenspurg" : "Regensburg",
        "Reimers" : "Altona",
        "Rostochii" : "Rostock",
        "Rothenburg <Tauber>" : "Rothenburg ob der Tauber",
        "Rothenburg o. d. Tauber" : "Rothenburg ob der Tauber",
        "Rothenburg o.d. Tauber" : "Rothenburg ob der Tauber",
        "Rothenburg" : "Rothenburg ob der Tauber",
        "Rothenburg, Tauber" : "Rothenburg ob der Tauber",
        "Rodolstadt" : "Rudolstadt",
        "Roma" : "Rom",
        "Saint Petersburg" : "Sankt Petersburg",
        "St. Petersburg" : "Sankt Petersburg",
        "Sankt-Peterburg" : "Sankt Petersburg",
        "Leningrad" : "Sankt Petersburg",
        "Petrograd" : "Sankt Petersburg",
        "Stargard" : "Stargard in Pommern",
        "Stargard Szczeciński" : "Stargard in Pommern",
        "Stargard Szczeciński" : "Stargard in Pommern",
        "Saalfeld/Saale" : "Saalfeld",
        "Schneeberg, Erzgebirgskreis" : "Schneeberg",
        "Schneeberg (Erzgebirgskreis)" : "Schneeberg",
        "Schorndorf (Rems-Murr-Kreis)" : "Schorndorf",
        "Stargard in Pommern" : "Stargard",
        "Stargard Szczeciński" : "Stargard",
        "Statthagen" : "Stadthagen",
        "Steinau" : "Steinau an der Oder",
        "Steinau, Oder" : "Steinau an der Oder",
        "Stetin" : "Stettin",
        "Stolberg/Harz" : "Stolberg",
        "Strasbourg" : "Straßburg",
        "Strassburg" : "Straßburg",
        "Stra\ss\\burg" : "Straßburg",
        "Schweidnitz" : "Świdnica",
        "Świdnica" : "Świdnica",
        "Argentorati" : "Straßburg",
        "Sulzbach, Oberpfalz" : "Sulzbach",
        "Toruń" : "Thorn",
        "Torun" : "Thorn",
        "Ülzen" : "Uelzen",
        "Wangen" : "Wangen im Allgäu",
        "Wallstadt [i.e. Frankfurt, Main " : "Frankfurt am Main",
        "Warszawa" : "Warschau",
        "Warszava" : "Warschau",
        "Weißenburg" : "Weißenburg in Bayern",
        "Weißenburg (Elsaß)" : "Wissembourg",
        "Weissenfels" : "Weißenfels",
        "Weißenfels <Halle, Saale>" : "Weißenfels",
        "Wilhelmsdorf" : "Wilhermsdorf",
        "Wilna" : "Vilnius",
        "wittenberg" : "Wittenberg",
        "Wittenberg4033 Wittenberg" : "Wittenberg",
        "Wittenbergae" : "Wittenberg",
        "Wolffenbüttel" : "Wolfenbüttel",
        "Wollgast" : "Wolgast",
        "Wroclaw" : "Breslau",
        "Wrocław" : "Breslau",
        "Ysni" : "Isny",
        "Zelle" : "Celle",
        "Zerbst/Anhalt" : "Zerbst",
        "Zugl.: Frankfurt <Oder>" : "Frankfurt (Oder)",
        "Züllichow" : "Züllichau",
        "öln" : "Köln",
        "'s-Gravenhage" : "Den Haag",
        "'s Gravenhage" : "Den Haag"
        }
    try:
        placeName = conc[placeName]
    except:
        pass
    return(placeName)
    """ Weiterer Korrekturbedarf:
    {'[fingiert]', '|bema|*ad*Digitalisierung UB Leipzig$2014-2016', 'helmstedt', 'fingiert [?]', 'Stargard in Pommern', 'fingiert?', 'fingiert', '[S.l.]', 'Freystadt', 'Text lat.', 'Mülheim', 'Etzelbach', 'Philadelphia?', 'Cölln', 'Lingen', '[Fingiert]', 'Magdebvrg', 'Fingiert', 'Elbingen', 'Nürnbeg', 'fingiert ?', '?', 'Freiburg in Schlesien', 'Bad Buchau', 'Nehrling', 'Tournon-sur-Rhône', 'Piemont', 'Lindau, Bodensee', '1', '[s.l.]'}
    """
def get_geodata_getty(id):
    root = get_getty_tree(id)
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
def get_getty_tree(id):
    url = "https://ref.de.dariah.eu/tgnsearch/tgnquery.xql?id=" + id
    fileobject = ul.urlopen(url, None, 10)
    tree = et.parse(fileobject)
    root = tree.getroot()
    return(root)
def get_getty_label(id):
    root = get_getty_tree(id)
    labelNode = root.find('.//{http://textgrid.info/namespaces/vocabularies/tgn}Preferred_Term/{http://textgrid.info/namespaces/vocabularies/tgn}Term_Text')
    try:
        label = labelNode.text.strip()
    except:
        return(None)
    return(label)
def get_geodata_gnd(id):
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