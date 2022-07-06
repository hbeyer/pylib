#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re

class Isil:
    bib_list = {
        "DE-1" : { 
            "bib" : "Staatsbibliothek zu Berlin - Preußischer Kulturbesitz", 
            "place" : "Berlin", 
            "gettyPlace" : "7003712", 
            "long" : "13.391458", 
            "lat" : "52.518425"
            },
        # "DE-01" lässt sich aus irgendeinem Grund nicht in "DE-1" umrechnen
        "DE-01" : { 
            "bib" : "Staatsbibliothek zu Berlin - Preußischer Kulturbesitz", 
            "place" : "Berlin", 
            "gettyPlace" : "7003712", 
            "long" : "13.391458", 
            "lat" : "52.518425"
            },
        "DE-3" : { 
            "bib" : "Universitäts- und Landesbibliothek Sachsen-Anhalt", 
            "place" : "Halle (Saale)", 
            "gettyPlace" : "1036898", 
            "long" : "11.970288", 
            "lat" : "51.489599"  
            },
        "DE-7" : { 
			"bib" : "Niedersächsische Staats- und Universitätsbibliothek Göttingen", 
			"place" : "Göttingen", 
			"gettyPlace" : "7005246", 
			"long" : "9.935913", 
			"lat" : "51.539524"  
			},
        "DE-8" : { 
			"bib" : "Universitätsbibliothek Kiel, Zentralbibliothek", 
			"place" : "Kiel", 
			"gettyPlace" : "7004457", 
			"long" : "10.110174", 
			"lat" : "54.346826"  
			},
        "DE-9" : { 
			"bib" : "Universitätsbibliothek Greifswald", 
			"place" : "Greifswald", 
			"gettyPlace" : "7004725", 
			"long" : "13.406214", 
			"lat" : "54.090714"  
		},
        "DE-11" : { 
			"bib" : "Humboldt-Universität zu Berlin, Universitätsbibliothek, Jacob-und-Wilhelm-Grimm-Zentrum", 
			"place" : "Berlin", 
			"gettyPlace" : "7003712", 
			"long" : "13.391036", 
			"lat" : "52.520452"  
			},        
        "DE-12" : { 
			"bib" : "Bayerische Staatsbibliothek", 
			"place" : "München", 
			"gettyPlace" : "7004333", 
			"long" : "11.580306", 
			"lat" : "48.147477"  
			},
        "DE-14" : { 
			"bib" : "Sächsische Landesbibliothek - Staats- und Universitätsbibliothek Dresden", 
			"place" : "Dresden", 
			"gettyPlace" : "7004455", 
			"long" : "13.736984", 
			"lat" : "51.028655" },        
        "DE-15" : { 
			"bib" : "Universitätsbibliothek Leipzig", 
			"place" : "Leipzig", 
			"gettyPlace" : "7012329", 
			"long" : "12.368251", 
			"lat" : "51.332328"
            },        
        "DE-16" : { 
			"bib" : "Universitätsbibliothek Heidelberg", 
			"place" : "Heidelberg", 
			"gettyPlace" : "7005177", 
			"long" : "8.705764", 
			"lat" : "49.409743"  
			},
        "DE-17" : { 
			"bib" : "TU Darmstadt, Universitäts- und Landesbibliothek", 
			"place" : "Darmstadt", 
			"gettyPlace" : "7004428", 
			"long" : "8.657725", 
			"lat" : "49.876453"  
			},
        "DE-18" : { 
			"bib" : "Staats- und Universitätsbibliothek Hamburg Carl von Ossietzky", 
			"place" : "Hamburg", 
			"gettyPlace" : "7004428", 
			"long" : "8.657789", 
			"lat" : "49.876654"  
			},
        "DE-19" : { 
			"bib" : "Universitätsbibliothek der LMU München", 
			"place" : "München", 
			"gettyPlace" : "7004333", 
			"long" : "11.580671", 
			"lat" : "48.150121"  
			},
        "DE-21" : { 
			"bib" : "Universitätsbibliothek der Eberhard Karls Universität", 
			"place" : "Tübingen", 
			"gettyPlace" : "7004426", 
			"long" : "9.061842", 
			"lat" : "48.525285"  
			},
        "DE-22" : { 
            "bib" : "Staatsbibliothek Bamberg", 
            "place" : "Bamberg", 
            "gettyPlace" : "7004325", 
            "long" : "10.882314", 
            "lat" : "49.891832"  
            },
        "DE-31" : { 
			"bib" : "Badische Landesbibliothek", 
			"place" : "Karlsruhe", 
			"gettyPlace" : "1003175", 
			"long" : "8.398831", 
			"lat" : "49.007957"  
			},
        "DE-23" : { 
			"bib" : "Herzog August Bibliothek Wolfenbüttel", 
			"place" : "Wolfenbüttel", 
			"gettyPlace" : "7005253", 
			"long" : "10.530302", 
			"lat" : "52.164293"  
			},
        "DE-24" : { 
			"bib" : "Württembergische Landesbibliothek", 
			"place" : "Stuttgart", 
			"gettyPlace" : "7004425", 
			"long" : "9.184828", 
			"lat" : "48.777219"  
			},
        "DE-27" : { 
			"bib" : "Thüringer Universitäts- und Landesbibliothek", 
			"place" : "Jena", 
			"gettyPlace" : "7005973", 
			"long" : "11.587734", 
			"lat" : "50.930590"  
			},
        "DE-28" : { 
			"bib" : "Universitätsbibliothek Rostock", 
			"place" : "Rostock", 
			"gettyPlace" : "7004717", 
			"long" : "12.134044", 
			"lat" : "54.086920"  
			},
        "DE-29" : { 
			"bib" : "Universitätsbibliothek Erlangen-Nürnberg", 
			"place" : "Erlangen", 
			"gettyPlace" : "7004332", 
			"long" : "11.007534", 
			"lat" : "49.596668"  
			},
        "DE-30" : { 
			"bib" : "Universitätsbibliothek J. C. Senckenberg, Zentralbibliothek", 
			"place" : "Frankfurt am Main", 
			"gettyPlace" : "7005293", 
			"long" : "8.652997", 
			"lat" : "50.120516"  
			},
        "DE-32" : { 
			"bib" : "Klassik Stiftung Weimar / Herzogin Anna Amalia Bibliothek", 
			"place" : "Weimar", 
			"gettyPlace" : "7012886", 
			"long" : "11.330919", 
			"lat" : "50.979618"  
			},
        "DE-33" : { 
			"bib" : "Landesbibliothek Mecklenburg-Vorpommern Günther Uecker im Landesamt für Kultur und Denkmalpflege", 
			"place" : "Schwerin", 
			"gettyPlace" : "7004433", 
			"long" : "11.414775", 
			"lat" : "53.616162"  
			},
        "DE-35" : { 
			"bib" : "Gottfried Wilhelm Leibniz Bibliothek - Niedersächsische Landesbibliothek", 
			"place" : "Hannover", 
			"gettyPlace" : "7013260", 
			"long" : "9.731263", 
			"lat" : "52.365288"  
			},
        "DE-36" : { 
			"bib" : "Wissenschaftliche Stadtbibliothek", 
			"place" : "Mainz", 
			"gettyPlace" : "7004449", 
			"long" : "8.269223", 
			"lat" : "50.008582"  
			},
        "DE-37" : { 
			"bib" : "Staats- und Stadtbibliothek Augsburg", 
			"place" : "Augsburg", 
			"gettyPlace" : "7004324", 
			"long" : "10.890646", 
			"lat" : "48.369518"
			},            
        "DE-39" : { 
			"bib" : "Forschungsbibliothek Gotha", 
			"place" : "Gotha", 
			"gettyPlace" : "7005938", 
			"long" : "10.704693", 
			"lat" : "50.945326"  
			},
        "DE-56" : { 
			"bib" : "Stadtbibliothek Braunschweig", 
			"place" : "Braunschweig", 
			"gettyPlace" : "7004434", 
			"long" : "10.527258", 
			"lat" : "52.262965"  
			},
        "DE-69" : { 
			"bib" : "Stadtbibliothek Koblenz", 
			"place" : "Koblenz", 
			"gettyPlace" : "7004448", 
			"long" : "7.596427", 
			"lat" : "50.358723"  
			},
        "DE-70" : { 
			"bib" : "Landesbibliothek Coburg", 
			"place" : "Coburg", 
			"gettyPlace" : "7004330", 
			"long" : "10.967095", 
			"lat" : "50.258028"  
			},
        "DE-75" : { 
			"bib" : "Stadtbibliothek im Bildungscampus Nürnberg", 
			"place" : "Nürnberg", 
			"gettyPlace" : "7004334", 
			"long" : "11.082657", 
			"lat" : "49.451877"  
			},
        "DE-107" : { 
			"bib" : "Landesbibliothekszentrum Rheinland-Pfalz / Pfälzische Landesbibliothek", 
			"place" : "Speyer", 
			"gettyPlace" : "7012341", 
			"long" : "8.415533", 
			"lat" : "49.315138"  
			},
        "DE-115" : { 
			"bib" : "Stadtbibliothek Hannover", 
			"place" : "Hannover", 
			"gettyPlace" : "7013260", 
			"long" : "9.745171", 
			"lat" : "52.366864"  
			},
        "DE-125" : { 
			"bib" : "Ratsschulbibliothek, Wissenschaftliche Bibliothek", 
			"place" : "Zwickau", 
			"gettyPlace" : "7012354", 
			"long" : "12.487368", 
			"lat" : "50.725059"  
			},
        "DE-154" : { 
			"bib" : "Staatliche Bibliothek Passau", 
			"place" : "Passau", 
			"gettyPlace" : "7004407", 
			"long" : "13.470771", 
			"lat" : "48.574316"  
			},
        "DE-155" : { 
			"bib" : "Staatliche Bibliothek Regensburg", 
			"place" : "Regensburg", 
			"gettyPlace" : "7013496", 
			"long" : "12.090811", 
			"lat" : "49.018406"  
			},
        "DE-211" : { 
			"bib" : "Erzbischöfliche Akademische Bibliothek Paderborn", 
			"place" : "Paderborn", 
			"gettyPlace" : "", 
			"long" : "13.3333", 
			"lat" : "52.9833"  
			},
        "DE-235" : { 
			"bib" : "Wissenschaftliche Stadtbibliothek Ingolstadt", 
			"place" : "Ingolstadt", 
			"gettyPlace" : "7017035", 
			"long" : "11.416301", 
			"lat" : "48.767614"  
			},
        "DE-294" : { 
			"bib" : "Ruhr-Universität Bochum, Universitätsbibliothek", 
			"place" : "Bochum", 
			"gettyPlace" : "7213248", 
			"long" : "7.260866", 
			"lat" : "51.445089"  
			},
        "DE-384" : { 
			"bib" : "Universitätsbibliothek Augsburg", 
			"place" : "Augsburg", 
			"gettyPlace" : "7004324", 
			"long" : "10.895144", 
			"lat" : "48.334518"  
			},
        "DE-537" : { 
			"bib" : "Stadtbibliothek Zehdenick", 
			"place" : "Zehdenick", 
			"gettyPlace" : "1038049", 
			"long" : "13.329211", 
			"lat" : "52.974251"  
			},
        "DE-547" : { 
			"bib" : "Forschungsbibliothek Gotha", 
			"place" : "Gotha", 
			"gettyPlace" : "7005938", 
			"long" : "10.704479", 
			"lat" : "50.945292"  
			},
        "DE-824" : { 
			"bib" : "Universitätsbibliothek Eichstätt-Ingolstadt", 
			"place" : "Eichstätt", 
			"gettyPlace" : "7004613", 
			"long" : "11.191754", 
			"lat" : "48.886671"  
			},
        "DE-2863" : { 
			"bib" : "Kirchenbibliothek Pegau", 
			"place" : "Pegau", 
			"gettyPlace" : "7012856", 
			"long" : "12.253089", 
			"lat" : "51.166823"  
			},
        "DE-3086" : { 
			"bib" : "Kirchenbibliothek Annaberg-Buchholz", 
			"place" : "Annaberg-Buchholz", 
			"gettyPlace" : "7012791", 
			"long" : "13.004864", 
			"lat" : "50.579261"  
			},
        "DE-Em2" : { 
			"bib" : "Johannes a Lasco Bibliothek Große Kirche Emden", 
			"place" : "Emden", 
			"gettyPlace" : "7005300", 
			"long" : "7.202364", 
			"lat" : "53.365412"   
			},
        "DE-Hel1" : { 
			"bib" : "Ehemalige Universitätsbibliothek", 
			"place" : "Helmstedt", 
			"gettyPlace" : "7005247", 
			"long" : "11.008745", 
			"lat" : "52.228761"  
			},
        "DE-B791" : { 
			"bib" : "Bundesverwaltungsgericht, Bibliothek", 
			"place" : "Leipzig", 
			"gettyPlace" : "", 
			"long" : "12.369873", 
			"lat" : "51.333104"  
			},
        "DE-F42" : { 
			"bib" : "Philosophisch-Theologische Hochschule Sankt Georgen, Bibliothek", 
			"place" : "Frankfurt am Main", 
			"gettyPlace" : "", 
			"long" : "8.713434", 
			"lat" : "50.099112"  
			},
        "DE-MUS-621612" : { 
			"bib" : "Bibliothek der St. Nikolai-Kirche Spandau", 
			"place" : "Berlin-Spandau", 
			"gettyPlace" : "7097050", 
			"long" : "13.205180", 
			"lat" : "52.538345"  
			},
        "DE-Zw1" : { 
			"bib" : "Landesbibliothekszentrum Rheinland-Pfalz / Bibliotheca Bipontina", 
			"place" : "Zweibrücken", 
			"gettyPlace" : "7012352", 
			"long" : "7.366376", 
			"lat" : "49.248678"
			},            
        "AT-HBTL" : { 
			"bib" : "Diözesan- und Universitätsbibliothek der Katholischen Privatuniversität Linz", 
			"place" : "Linz", 
			"gettyPlace" : "7003199", 
			"long" : "14.291722", 
			"lat" : "48.303904"  
			},        
        "AT-OeNB" : { 
			"bib" : "Österreichische Nationalbibliothek", 
			"place" : "Wien", 
			"gettyPlace" : "", 
			"long" : "16.366962", 
			"lat" : "48.206343"  
			},        
        "#SBBW" : { 
			"bib" : "Spezialbibliothek der Bundeswehr", 
			"place" : "Verschiedene", 
			"gettyPlace" : "", 
			"long" : "", 
			"lat" : ""  
			},        
        "#GMG" : { 
			"bib" : "Bibliothek des Geistlichen Ministeriums Greifswald", 
			"place" : "Greifswald", 
			"gettyPlace" : "7004725", 
			"long" : "13.377507, ", 
			"lat" : "54.095509"  
			},
        "#VD17R" : { 
			"bib" : "VD17-Redaktion", 
			"place" : "Verschiedene", 
			"gettyPlace" : "", 
			"long" : "", 
			"lat" : ""  
			},
        "#KBROEHR" : { 
			"bib" : "Kirchenbibliothek Röhrsdorf", 
			"place" : "Röhrsdorf", 
			"gettyPlace" : "7111557", 
			"long" : "13.524941", 
			"lat" : "51.095493"  
			},
        "#THURKB" : { 
			"bib" : "Thüringische Kirchenbibliotheken", 
			"place" : "Thüringen", 
			"gettyPlace" : "7003689", 
			"long" : "11.012385", 
			"lat" : "50.931662" 
            }
    }
    eln_isil = {
        "0000" : "#VD17R",
        "0001" : "DE-01",
        "0003" : "DE-3",
        "0007" : "DE-7",
        "0008" : "DE-8",
        "0009" : "DE-9",
        "0011" : "DE-11",
        "0012" : "DE-12",
        "0014" : "DE-14",
        "0015" : "DE-15",
        "0016" : "DE-16",
        "0017" : "DE-17",
        "0018" : "DE-18",
        "0019" : "DE-19",
        "0021" : "DE-21",
        "0023" : "DE-23",
        "0024" : "DE-24",
        "0027" : "DE-27",
        "0028" : "DE-28",
        "0029" : "DE-29",
        "0030" : "DE-30",
        "0031" : "DE-31",
        "0032" : "DE-32",
        "0033" : "DE-33",
        "0035" : "DE-35",
        "0036" : "DE-36",
        "0039" : "DE-39",
        "0056" : "DE-56",
        "0069" : "DE-69",
        "0070" : "DE-70",
        "0075" : "DE-75",
        "0107" : "DE-107",
        "0115" : "DE-115",
        "0125" : "DE-125",
        "0155" : "DE-155",
        "0211" : "DE-211",
        "0294" : "DE-294",
        "0384" : "DE-384",
        "0547" : "DE-547",
        "0547/0039" : "DE-537",
        "0824" : "DE-824",
        "1999" : "#VD17R",
        "2028" : "DE-32",
        "20301" : "DE-14",
        "20355" : "DE-15",
        "20357" : "DE-16",
        "20729" : "DE-31",
        "21881" : "DE-125",
        "3122" : "DE-Hel1",
        "3206" : "Thüringische",
        "3614" : "DE-F42",
        "3703" : "DE-Em2",
        "3703/0002" : "DE-Em2",
        "40004" : "DE-12",
        "40005" : "DE-17",
        "40006" : "DE-19",
        "40046" : "DE-155",
        "40074" : "DE-824",
        "40082" : "DE-F42",
        "4369" : "DE-4369",
        "4620" : "#VD17R",
        "5002" : "DE-MUS-621612",
        "5007" : "AT-HBTL",
        "5051" : "DE-B791",
        "5113" : "#KBROEHR",
        "5119" : "#SBBW",
        "5120" : "#GMG",
        "9511" : "AT-OeNB",
        "DDSU" : "DE-14",
        "DE-01" : "DE-1", # Das hier hat aus irgendeinem Grund keinen Effekt
        "HDUB" : "DE-16", 
        "KALB" : "DE-31",
        "L1BV" : "DE-B791",
        "L1PGKB" : "DE-2863",
        "L1UB" : "DE-15",
        "TUUB" : "DE-21"
    }
    iln_isil = {
        "11" : "DE-1",# SBB Berlin 1a
        "39" : "DE-547", # FB Gotha
        "50" : "DE-23", # HAB
        "62" : "DE-28", # UB Rostock
        "65" : "DE-3",  # ULB Halle
        "78" : "DE-115", # SB Hannover
        "620" : "#VD17R",
        "755" : "#THURKB", # Thüringische Kirchenbibliotheken
        "2001" : "DE-21", # UB Tübingen
        "2006" : "DE-14", # UB Dresden
        "2008" : "DE-24", # WLB Stuttgart
        "2010" : "DE-15", # UB Leipzig
        "2011" : "DE-16", # UB Heidelberg
        "2018" : "DE-31", # BLB Karlsruhe
        "2051" : "DE-B791", # BVG Leipzig
        "2396" : "DE-Zw1", # LBZ Rh.-Pf. Bibliotheca Bipontina
        "2527" : "DE-125", # RSB Zwickau
        "2541" : "DE-2863", # KB Pegau
        "2556" : "DE-3086", # KB Annaberg-Buchholz
        "4002" : "DE-MUS-621612", # St. Nikolai Spandau
        "4012" : "DE-12", # BSB
        "4036" : "DE-17", # UB Darmstadt
        "4082" : "DE-30", # UB Frankfurt am Main
        "4112" : "DE-29", # UB Erlangen-Nürnberg
        "4126" : "DE-384", # UB Augsburg
        "4299" : "DE-75", # STB Nürnberg
        "4302" : "DE-107", # Pf. LB Speyer
        "4346" : "DE-70", # LB Coburg
        "4385" : "DE-F42", # St. Georgen
        "4394" : "DE-235", #SB Ingolstadt
        "4395" : "DE-37", # StUB Augsburg
        "4396" : "DE-22", #StB Bamberg
        "4397" : "DE-154", # StB Passau
        "5113" : "#KBROEHR", # Kirchenbibliothek Röhrsdorf
        "5120" : "#GMG" # Geistliches Ministerium Greifswald        
    }

def get_isil(id, type = "iln"):
    if type == "iln":
        try:
            return(Isil.iln_isil[id])
        except:
            return(None)
    elif type == "eln":
        try:
            return(Isil.eln_isil[id])
        except:
            return(None)
    return(None)

def get_bib(id, type = "isil"):
    if type == "isil":
        try:
            return(Isil.bib_list[id])
        except:
            return(None)
    elif type in ["iln", "eln"]:
        isil = get_isil(id, type)
        if isil == False:
            return(None)
        try:
            return(Isil.bib_list[isil])
        except:
            return(None)