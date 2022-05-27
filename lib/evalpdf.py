#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pdfplumber
import re
import os.path
import logging
from lib import duennhaupt as dh
logging.basicConfig()


class Evaluation:
    index = {}
    path = ""
    sww = []
    rexx = []
    def __init__(self, path = None, sww = None, rexx = None):
        if path != None:
            self.path = path
        if sww != None:
            self.sww = sww
        if rexx != None:
            self.rexx = rexx
    def eval(self):
        if os.path.exists(self.path) == False:
            logging.error(f"Ungültiger Pfad: {self.path}")
            return(None)
        if self.sww == [] and self.rexx == []:
            logging.error("Keine Suchwörter übergeben")
            return(None)
        with pdfplumber.open(self.path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                pn = str(page.page_number)
                text = text.replace("\n", " ")
                text = text.replace("- ", "")
                for sw in self.sww:
                    if sw in text.lower():
                        try:
                            self.index[sw].append(pn)
                        except:
                            self.index[sw] = [pn]
                for name, rex in self.rexx:
                    test = re.search(rex, text)
                    if test != None:
                        try:
                            self.index[name].append(pn)
                        except:
                            self.index[name] = [pn]
            return(True)
    def __str__(self):
        ret = f"SDD-Evaluation für {self.path}"
        for label, pages in self.index.items():
            ret = ret + f"\n{label}: {', '.join(pages)}"
        return(ret)

class EvaluationSDD(Evaluation):
    def __init__(self, path):
        super().__init__()
        self.path = path
        # Liste zu ergänzen
        self.sww = [ "dünnhaupt", "alchem", "emblem", "wolfenbüttel", "braunschweig", "lüneburg",
            "helmstedt", "conring"]
        duenn = dh.get_query_words()
        self.sww.extend(duenn)
        self.rexx = [("17. Jh.", r"16\d\d")]



# Dokumentation: https://github.com/jsvine/pdfplumber