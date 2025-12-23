#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import logging
import glob
import pdfplumber
from lib import csvt
from datetime import datetime

# Diese Extraktion funktioniert ab BNB-Ausgabe 2023-11-27
class Entry:
    def __init__(self, text = None):
        self.text = ""
        if text != None:
            self.text = text        
        self.dewey = ""
        self.isbn = ""
        self.bnb_number = ""
        self.title = ""
        self.imprint = ""
        self.place = ""
        self.publisher = ""
        self.year = ""
        self.price = ""
        self.phys_descr = ""
        self.pub_type = ""
        self.topical_terms = ""
        self.get_dewey()
        self.get_isbn()
        self.get_bnb_num()
        self.get_title()
        self.get_imprint()
        self.get_price()
        self.get_phys_descr()
        self.get_pub_type()
    def get_dewey(self):
        extr = re.search(r"DDC (\d{3}(\.\d+)?)", self.text)
        try:
            self.dewey = extr.group(1)
        except:
            pass
    def get_isbn(self):
        extr = re.search(r"ISBN (97[89]\d+)", self.text)
        try:
            self.isbn = extr.group(1)
        except:
            pass
    def get_bnb_num(self):
        extr = re.search(r"BNB NUMBER (GB[A-Z0-9]{7})", self.text)
        try:
            self.bnb_number = extr.group(1)
        except:
            pass
    def get_title(self):
        extr = re.search(r"TITLE (.+)[\s\.]+IMPRINT", self.text)
        try:
            self.title = extr.group(1)
        except:
            pass
    def get_imprint(self):
        extr = re.search(r"IMPRINT ([^:]+) : (.+), \[?(20\d\d)\]?", self.text)
        try:
            self.imprint = extr.group(0)
        except:
            pass
        else:
            self.place = extr.group(1)
            self.publisher = extr.group(2)
            self.year = extr.group(3)
    def get_price(self):
        extr = re.search(r"(£\d+\.\d{2})", self.text)
        try:
            self.price = extr.group(1)
        except:
            pass
    def get_phys_descr(self):
        extr = re.search(r"PHYSICAL DESCRIPTION (.+)", self.text)
        try:
            phys_etc = extr.group(1)
        except:
            pass
        else:
            parts = phys_etc.split("TOPICAL TERMS")
            self.phys_descr = parts.pop(0)
            self.topical_terms = "".join(parts).replace("  ", " ").strip()
    def get_pub_type(self):
        extr = re.search(f"{self.isbn} (ePub ebook|Kindle ebook|PDF ebook|ebook|paperback|hardback|spiral-bound)", self.text)
        try:
            self.pub_type = extr.group(1)
        except:
            pass
    @classmethod
    def get_fields(self):
        return(["BNB-Number", "ISBN", "Price", "DDC", "Title", "Place", "Publisher", "Year", "Pub_type", "Phys_descr", "Topics"])
    def to_row(self):
        return([self.bnb_number, self.isbn, self.price, self.dewey, self.title, self.place, self.publisher, self.year, self.pub_type, self.phys_descr, self.topical_terms])  
        
class QuarterTable:
    def __init__(self, year, quarter, regex_dewey = None):
        if re.match(r"^20\d\d$", year) == None:
            logging.error("Kein korrektes Jahr angegeben (ab 2023 als String)")
            return
        self.year = year
        if quarter not in ["1", "2", "3", "4", "X"]:
            logging.error("Kein korrektes Quartal angegeben (1, 2, 3 oder 4 als String)")
        self.quarter = quarter
        quart_expr = { "1" : "0[1-3]", "2" : "0[4-6]", "3" : "0[789]", "4" : "1[012]", "X" : "[0-9]*" }
        date_expr = f"{self.year}-{quart_expr[self.quarter]}-*"
        self.path = f"//server/Nationalbibliographien/BNB/{date_expr}.pdf"
        #regex_dewey = r"^1\d\d|^[48]9[1-7]"
        self.regex_dewey = r"^\d"
        if regex_dewey != None:
            self.regex_dewey = regex_dewey
        fields = Entry.get_fields()
        self.tab = csvt.Table(fields)
    def get_data(self):
        self.files = glob.glob(self.path)
        for path in self.files:
            entries = []
            cont_text = ""
            with pdfplumber.open(path) as pdf:
                for count, page in enumerate(pdf.pages):
                    left = page.crop((0, 70, 0.5 * page.width, 0.9 * page.height))
                    right = page.crop((0.5 * page.width, 70, page.width, page.height))
                    text_l = left.extract_text()
                    text_r = right.extract_text()        
                    pn = str(page.page_number)
                    cont_text = cont_text + text_l + text_r
                    print(f"Datei {path}, Seite {pn} verarbeitet.")
                pieces = cont_text.split("PREPUBLICATION RECORD")
                pieces = list(map(prepare_text, pieces))
                print(f"{len(pieces)} Einträge extrahiert.")
                for piece in pieces:
                    entry = Entry(piece)
                    if re.match(self.regex_dewey, entry.dewey):
                        row = entry.to_row()
                        self.tab.content.append(row)
                        print(f"{entry.bnb_number}")
    def save(self, target_folder = None):
        if len(self.tab.content) == 0:
            logging.error("Es wurden keine Daten extrahiert.")
            return(False)
        if target_folder == None:
            target_folder = ""
        self.tab.save(f"{target_folder}BNB-Tabelle-{self.year}-Q{self.quarter}")
        return(True)
        
class CustomTable(QuarterTable):
    def __init__(self, glob_date = None, regex_dewey = None, path_pdfs = None):
        if glob_date == None:
            glob_date = "*"
        self.regex_dewey = r"^\d"
        if regex_dewey != None:
            self.regex_dewey = regex_dewey
        fields = Entry.get_fields()
        self.tab = csvt.Table(fields)
        if path_pdfs == None:
            path_pdfs = "//server/Nationalbibliographien/BNB/"
        self.path = f"{path_pdfs}{glob_date}.pdf"
    def save(self, target_folder = None):
        if len(self.tab.content) == 0:
            logging.error("Es wurden keine Daten extrahiert.")
            return(False)
        if target_folder == None:
            target_folder = ""
        path = f"{target_folder}BNB-Tabelle-Personalisiert"
        self.tab.save(path)
        print(f"Es wurde eine Tabelle zum Zeitraum {self.regex_date}, eingeschränkt auf DDC {self.regex_dewey} abgespeichert unter {path}")
        return(True)        
    

def prepare_text(text):
    text = text.replace("\n", " ")
    text = text.replace("  ", " ")
    text = text.strip()
    return(text)