#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
from lib import csvt
          
class DB():
    def __init__(self):
        self.tab = csvt.Table()
        self.tab.load("K10plus-Bibliotheken.csv")
        self.index_isil = {}
        self.index_eln = {}
        for num, row in enumerate(self.tab.content):
            isil, iln, eln, _bib, _addr, _plz, _place, _state, _country, _lat, _long, _website, _opac = row
            if isil != "":
                self.index_isil[isil] = num
            self.index_eln[eln] = num
    def get_by_isil(self, isil):
        try:
            return(self.tab.content[self.index_isil[isil]])
        except:
            try:
                data = self.isil_vd17[isil]
            except:
                return(None)
            else:
                return([isil, data["iln"], data["eln"], data["bib"], "", "", data["place"], "", "", data["long"], data["lat"], "", ""])
    def get_by_eln(self, eln):
        eln = self.replace_eln(eln)
        try:
            return(self.tab.content[self.index_eln[eln]])
        except:
            try:
                return(self.tab.content[self.index_isil[Isil.eln_isil[eln]]])
            except:
                return(None)
    def replace_eln(self, eln):
        conc = {
            "20728" : "BSZ",
            "100019999" : "99999999",
            "20301" : "DDSU",
            "0014" : "DDSU",
            "0012" : "40004",
            "20355" : "L1UB",
            "2011" : "HDUB",
            "20357" : "HDUB",
            "40082" : "3614",
            "21881" : "C1ZWRB",
            "40013" : "0030",
            "2018" : "KALB",
            "20729" : "KALB",
            "40034" : "0070",
            "21356" : "L1BV",
            "20001" : "TUUB",
            "40044" : "0107",
            "5120" : "3885/0004",
            "40008" : "0026",
            "0037" : "40059",
            "4680" : "SBZWBB",
            "20303" : "S1LB",
            "40009" : "0029",
            "100019999" : "BSZ"
        }
        try:
            return(conc[eln])
        except:
            return(eln)
    
    isil_vd17 = {
        "#SBBW" : { 
			"bib" : "Spezialbibliothek der Bundeswehr",
            "eln" : "5119",
            "iln" : "5119",
			"place" : "Verschiedene", 
			"gettyPlace" : "", 
			"long" : "", 
			"lat" : ""  
			},        
        "#GMG" : { 
			"bib" : "Bibliothek des Geistlichen Ministeriums Greifswald", 
            "eln" : "5120",
            "iln" : "5120",
			"place" : "Greifswald", 
			"gettyPlace" : "7004725", 
			"long" : "13.377507, ", 
			"lat" : "54.095509"  
			},
        "#VD17R" : { 
			"bib" : "VD17-Redaktion",
            "eln" : "4620",
            "iln" : "620",
			"place" : "Verschiedene", 
			"gettyPlace" : "", 
			"long" : "", 
			"lat" : ""  
			},
        "#VD17Polen" : { 
			"bib" : "Polnische Bibliotheken", 
            "eln" : "5122",
            "iln" : "1122",
			"place" : "Polen", 
			"gettyPlace" : "7006366", 
			"long" : "20.0000", 
			"lat" : "52.0000"  
			},        
        "#KBROEHR" : { 
			"bib" : "Kirchenbibliothek Röhrsdorf", 
			"place" : "Röhrsdorf", 
            "eln" : "5113",
            "iln" : "4113",
			"gettyPlace" : "7111557", 
			"long" : "13.524941", 
			"lat" : "51.095493"  
			},
        "#THURKB" : { 
			"bib" : "Thüringische Kirchenbibliotheken", 
            "eln" : "3206",
            "iln" : "755",
			"place" : "Thüringen", 
			"gettyPlace" : "7003689", 
			"long" : "11.012385", 
			"lat" : "50.931662" 
            },
        "#EKMD" : { 
			"bib" : "Evangelische Kirche Mitteldeutschland", 
            "eln" : "4030",
            "iln" : "1030",
			"place" : "Magdeburg", 
			"gettyPlace" : "7004456", 
			"long" : "11.634967", 
			"lat" : "52.124002" 
            }  
    }            