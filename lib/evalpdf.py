#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pdfplumber
import re
import os.path
import logging
from lib import duennhaupt as dh
from pdfminer.layout import LTTextLineHorizontal
from pdfminer.layout import LTTextBoxHorizontal
logging.basicConfig()


class Evaluation:
    index = {}
    contexts = {}
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
        if os.path.exists(self.path) == False:
            logging.error(f"Ungültiger Pfad: {self.path}")
        if self.sww == [] and self.rexx == []:
            logging.error("Keine Suchwörter übergeben")
    def eval(self):
        with pdfplumber.open(self.path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                text = prepare_text(text)
                pn = str(page.page_number)
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
    def eval_context(self):
        with pdfplumber.open(self.path, laparams={}) as pdf:
            for page in pdf.pages:
                layout = page.layout
                line = ""
                for element in layout: 
                    if isinstance(element, LTTextBoxHorizontal):
                        for el in element:
                            line = el.get_text()
                            self.eval_line(line)
                    elif isinstance(element, LTTextLineHorizontal):
                        line = element.get_text()
                        self.eval_line(line)
            return(True)
    def eval_line(self, line):
        line = prepare_text(line)
        for sw in self.sww:
            if sw in line:
                try:
                    self.contexts[sw].append(line)
                except:
                    self.contexts[sw] = [line]
        for name, rex in self.rexx:
            test = re.search(rex, line)
            if test != None:
                try:
                    self.contexts[name].append(line)
                except:
                    self.contexts[name] = [line]
    def __str__(self):
        ret = f"Evaluation für {self.path}"
        for label, pages in self.index.items():
            ret = ret + f"\n{label}: {', '.join(pages)}"
        for label, lines in self.contexts.items():
            ret = ret + f"\n{label}: {len(lines)} Treffer:"
            for line in lines:
                ret = ret + f"\n\t{line}"
            ret = ret + "\n"
        return(ret)

class EvaluationSDD(Evaluation):
    def __init__(self, path):
        #super().__init__()
        if path != None:
            self.path = path
        # Liste zu ergänzen
        self.sww = [ "dünnhaupt", "alchem", "emblem", "wolfenbüttel", "braunschweig", "lüneburg",
            "helmstedt", "conring"]
        duenn = dh.get_query_words()
        self.sww.extend(duenn)
        self.rexx = [("17. Jh.", r"16\d\d")]
        if os.path.exists(self.path) == False:
            logging.error(f"Ungültiger Pfad: {self.path}")
        if self.sww == [] and self.rexx == []:
            logging.error("Keine Suchwörter übergeben")        

def prepare_text(text):
    text = text.replace("\n", " ")
    text = text.replace("- ", "")
    return(text)


# Dokumentation: https://github.com/jsvine/pdfplumber
