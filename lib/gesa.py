#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ul
import re
import pickle
import logging
from lib import csvt
from lib import cache
    
class MultRequest():
    rexx = {
        "Name" :                "Verstorbene\(r\)\s*</td>\s*<td>\s*<span class='highlight0'>([^<]+)</span>",
        "Sterbejahr" :          "Sterbejahr\s*</td>\s*<td>\s*<a class='titel'[^>]+>([0-9]{4})</a>",
        "GND" :                 "pnd&amp;s1=([0-9X]+)",
        "Erscheinungsjahr" :    "Erscheinungsjahr\s*</td>\s*<td>\s*<a class='titel'[^>]+>([0-9]{4})</a>",
        "Druckort" :            "Druckort\s*</td>\s*<td>\s*<a class='titel'[^>]+>([^<]+)</a>",
        "Standort" :            "Standort\s*</td>\s*<td>\s*([^\r\n<]+)",
        "Signatur" :            "Signatur\s*</td>\s*<td>\s*([^\n]+)\s*</td>",
        "Katalognachweis" :     "Katalognachweis\s*</td>\s*<td>\s*([^<]+)\s*<br />"
    }
    def __init__(self, filter, limit = None):
        self.cache = cache.Cache("cache/GESA-Trefferlisten")
        self.cacheG = cache.CacheGESA()
        self.sources = SourceDB()
        self.offset = 0
        self.length = 30
        self.ids = set()
        self.data = []
        self.limit = 1000000
        if limit != None:
            self.limit = limit
        for num in range(self.limit):
            req = Request(filter, self.cache, self.offset, self.length)
            ids = req.get_numbers()
            len1 = len(self.ids)
            self.ids.update(ids)
            len2 = len(self.ids)
            if len1 == len2:
                logging.info(f"Abbruch: Anzahl der IDs hat sich nicht erhöht ({len1})")
                break
            self.offset += self.length
        with open('ids_gesa', 'wb') as file:
            pickle.dump(self.ids, file)
        logging.info(f"{len(self.ids)} IDs gefunden und in ids_gesa gespeichert")
    def grab_data(self, limit = None):
        if limit != None:
            self.limit = limit
        with open('ids_gesa','rb') as file:
            self.ids = pickle.load(file)
        for count, id in enumerate(self.ids):
            resp = self.cacheG.get_html(id)
            if resp == None:
                continue
            dataset = { "GESA-ID" : id }
            for field, pattern in self.rexx.items():
                try:
                    dataset[field] = re.search(pattern, resp, re.IGNORECASE).group(1)
                except:
                    dataset[field] = ""
            dataset["Stolberg"] = ""
            if dataset["Katalognachweis"] != "":
                if "Stolberg" in dataset["Katalognachweis"]:
                    dataset["Stolberg"] = "Ja"
                dataset["Katalognachweis"] = self.sources.get_id(dataset["Katalognachweis"])
            self.data.append(dataset)
            if count > self.limit:
                break
        return(True)
    def to_csv(self):
        fields = ["GESA-ID", "Stolberg"]
        fields.extend(self.rexx.keys())
        tab = csvt.Table(fields)
        for row in self.data:
            tab.content.append([row[field] for field in fields])
        tab.save("DataGrab-GESA")
        logging.info("Daten gespeichert unter DataGrab-GESA.csv")
        self.sources.to_csv()
        
class Request():
    def __init__(self, filter, cache, offset = None, length = None):
        # https://www.online.uni-marburg.de/fpmr/php/gs/xs3.php?lang=de&ex=fpmr&f1=name&f2=&f3=sj&s1=&s2=&s3=1600-1700&o=&b=AND&m=t&l=30&p=150
        self.filter = filter
        self.cache = cache
        self.offset = 1
        if offset != None:
            self.offset = offset
        self.length = 30
        if length != None:
            self.length = length        
        self.url = f"https://www.online.uni-marburg.de/fpmr/php/gs/xs3.php?lang=de&ex=fpmr&f1=name&f2=&f3=sj&s1=&s2=&s3={self.filter}&o=&b=AND&m=t&l={str(self.length)}&p={str(self.offset)}"
        self.response = cache.get_content(self.url, f"GESA_{self.offset}-{self.offset + self.length}")
        if self.response == None:
            logging.error(f"Keine Antwort von {self.url}")
    def get_numbers(self):
        num = re.findall(r"id\[\]=([0-9]+)&amp;", self.response, re.IGNORECASE)
        return(num)
        
class SourceDB():
    def __init__(self):
        self.content = []
    def get_id(self, name):
        name = name.strip()
        if name not in self.content:
            self.content.append(name)
        return(self.content.index(name))
    def to_csv(self):
        tab = csvt.Table(["ID", "Quelle"])
        for source in self.content:
            tab.content.append([self.content.index(source), source])
        tab.save("DataGrab-GESA_Quellenverzeichnis")
        logging.info("Quellen gespeichert unter DataGrab-GESA_Quellenverzeichnis.csv")
        
def alternate_pn(name):
    name = name.strip()
    name = name.replace("ue", "ü").replace("ae", "ä").replace("oe", "ö").replace("Oe", "Ö").replace("ss", "ß")
    conc = {
        "ALtenburg" : ["Altenburg"],
        "Caßel" : ["Kassel"],
        "Cöthen" : ["Köthen"],
        "Cüstrin" : ["Küstrin"],
        "Koburg" : ["Coburg"],
        "Colberg" : ["Kolberg"],
        "Cölln an der Spree" : ["Berlin"],
        "Cölln" : ["Berlin"],
        "Düßeldorf" : ["Düsseldorf"],
        "Frankfurt an der Oder" : ["Frankfurt, Oder", "Frankfurt, oder", "Frankfurt (Oder)"],
        "Frankfurt am Main" : ["Frankfurt"],
        "Groß-Glogau" : ["Glogau"],
        "Großglogau" : ["Glogau"],
        "Großen-Hain" : ["Großenhain"],
        "Großen-Hayn" : ["Großenhain"],
        "Hannoversch-Münden" : ["Münden"],
        "Halle an der Saale" : ["Halle, Saale"],
        "Heinrichstadt" : ["Wolfenbüttel"],
        "Lißa" : ["Leszno"],
        "Mülhausen" : ["Mühlhausen"],
        "Polnisch-Lißa" : ["Lissa", "Leszno"],
        "Rotenburg ob der Tauber" : ["Rotenburg", "Rothenburg"],
        "Schwäbisch-Hall" : ["Schwäbisch Hall"],
        "Stadthagen" : ["Statthagen 1616"],
        "Steinau an der Oder" : ["Steinau"],
        "Wolfenbüttel-Heinrichstadt" : ["Wolfenbüttel"],
        "Heinrichstadt-Wolfenbüttel" : ["Wolfenbüttel"],
        "Zelle" : ["Celle"]
    }
    try:
        return(conc[name])
    except:
        return([name])
        
def normalize_place(pname):
    conc = {
        "Berlin-Friedrichswerder" : "Berlin",
        "Brandenburg" : "Brandenburg an der Havel",
        "Cassel" : "Kassel",
        "Clausthal" : "Clausthal-Zellerfeld",
        "Coelln" : "Berlin",
        "Coelln an der Spree" : "Berlin",
        "Coethen" : "Köthen",
        "Colberg" : "Kolberg",
        "Cölln" : "Berlin",
        "Cölln an der Spree" : "Berlin",
        "Cöthen" : "Köthen",
        "Cuestrin" : "Küstrin",
        "Cüstrin" : "Küstrin",
        "Dorfchemnitz" : "Chemnitz",
        "Duesseldorf" : "Düsseldorf",
        "Frankfurt" : "Frankfurt am Main",
        "Frankfurt (Main)" : "Frankfurt am Main",
        "Frankfurt an der Oder" : "Frankfurt (Oder)",
        "Fuerth" : "Fürth",
        "Giessen" : "Gießen",
        "Glueckstadt" : "Glückstadt",
        "Goettingen" : "Göttingen",
        "Gothenburg" : "Gotenburg",
        "Gross-Glogau" : "Groß-Glogau",
        "Gross-Tschirnau" : "Groß-Tschirnau",
        "Grossen-Hain" : "Großenhain",
        "Grossen-Hayn" : "Großenhain",
        "Grossenhain" : "Großenhain",
        "Grossglogau" : "Groß-Glogau",
        "Guestrow" : "Güstrow",
        "Halle" : "Halle (Saale)",
        "Halle an der Saale" : "Halle (Saale)",
        "Hannoversch-Muenden" : "Mannoversch Münden",
        "Heinrichstadt" : "Wolfenbüttel",
        "Heinrichstadt-Wolfenbuettel" : "Wolfenbüttel",
        "Koburg" : "Coburg",
        "Koeln" : "Köln",
        "Koenigsberg" : "Königsberg",
        "Koethen" : "Köthen",
        "Königsberg in Preußen" : "Königsberg",
        "Kuestrin" : "Küstrin",
        "Luebeck" : "Lübeck",
        "Lueneburg" : "Lüneburg",
        "Muehlhausen" : "Mühlhausen/Thüringen",
        "Muehlhausen in Thueringen" : "Mühlhausen/Thüringen",
        "Muelhausen" : "Mülhausen",
        "Muenchberg" : "Münchberg",
        "Muenchen" : "München",
        "Neustadt am Aisch" : "Neustadt an der Aisch",
        "Neustadt-Magdeburg" : "Magdeburg",
        "Noerdlingen" : "Nördlingen",
        "Nuernberg" : "Nürnberg",
        "Oehringen" : "Öhringen",
        "Ohringen" : "Öhringen",
        "Osnabrueck" : "Osnabrück",
        "Ploen" : "Plön",
        "Polnisch Lissa" : "Lissa",
        "Polnisch-Lissa" : "Lissa",
        "Roemhild" : "Römhild",
        "Rotenburg ob der Tauber" : "Rothenburg ob der Tauber",
        "Salfeld" : "Saalfeld/Saale",
        "Schwäbisch-Hall" : "Schwäbisch Hall",
        "Schwaebisch-Hall" : "Schwäbisch Hall",
        "Stendel" : "Stendal",
        "Strassburg" : "Straßburg",
        "Tadenborn" : "Paderborn",
        "Tuebingen" : "Tübingen",
        "Upsala" : "Uppsala",
        "Vaesteras" : "Västeras",
        "Weissenfels" : "Weißenfels",
        "Wiborg" : "Wyborg",
        "Wilna" : "Vilnius",
        "Wolfenbuettel" : "Wolfenbüttel",
        "Wolfenbuettel-Heinrichstadt" : "Wolfenbüttel",
        "Wolfenbüttel-Heinrichstadt" : "Wolfenbüttel",
        "Wuerzburg" : "Würzburg",
        "Zelle" : "Celle",
        "Zuellichau" : "Züllichau",
        "Zweibruecken" : "Zweibrücken"
    }
    try:
        return(conc[pname])
    except:
        return(pname)