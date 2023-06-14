#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pdfplumber
import re
import os.path
import logging
from lib import duennhaupt as dh
from lib import csvt
from pdfminer.layout import LTTextLineHorizontal
from pdfminer.layout import LTTextBoxHorizontal
from itertools import groupby, count
logging.basicConfig()


class Evaluation:
    def __init__(self, path = None, sww = None, rexx = None):
        self.index = {}
        self.contexts = {}
        self.path = ""
        self.sww = []
        self.rexx = []
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
                    test = re.search(rex, text.lower())
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
            
# pers_terms, place_terms und subj_terms: Dictionary mit Lemmata und regulären Ausdrücken (nur Kleinbuchstaben)
class BookIndex:
    def __init__(self, path, pers_terms = None, place_terms = None, subj_terms = None):
        self.path = path
        self.pers_terms = None
        if pers_terms != None:
            self.pers_terms = pers_terms
        self.place_terms = None
        if place_terms != None:
            self.place_terms = place_terms
        self.subj_terms = None
        if subj_terms != None:
            self.subj_terms = subj_terms
    def build(self):
        if self.pers_terms != None:
            self.proceed_regex(self.pers_terms, "Personenregister")
        if self.place_terms != None:
            self.proceed_regex(self.place_terms, "Ortsregister")
        if self.subj_terms != None:
            self.proceed_regex(self.subj_terms, "Sachregister")
        return(True)
    def proceed_regex(self, terms, reg_name = None):
        if reg_name == None:
            reg_name = "Register_Regex"
        rexx = [(name, rex) for name, rex in terms.items()]
        reg = { value: key for key, value in terms.items() }
        ev = Evaluation(self.path, None, rexx)
        ev.eval()
        tab = csvt.Table(["Lemma", "Suchbegriff", "Seiten"])
        for label, pages in ev.index.items():
            tab.content.append([label, terms[label], ", ".join(pages)])
        tab.save(reg_name)
        return(True)

def prepare_text(text):
    text = text.replace("\n", " ")
    text = text.replace("- ", "")
    return(text)

# Formatiert eine durch Komma getrennte Zahlenreihe durch Einfügen von "f." und "-"
def format_numbers(numstr):
    pages = numstr.split(",")
    pages = [a.strip() for a in pages]
    collect = []
    lastnum = -1
    cache = []
    for num in pages:
        if num == "":
            continue
        if "-" in num:
            collect.extend(resolve(num))
            continue
        collect.append(int(num))
    groups = groupby(collect, key=lambda item, c=count():item-next(c))
    tmp = [list(g) for k, g in groups]
    printlist = []
    for item in tmp:
        if len(item) == 1:
            printlist.append(str(item[0]))
        elif len(item) == 2:
            printlist.append(str(item.pop(0)) + "f.")
        elif len(item) > 2:
            printlist.append(f"{str(item.pop(0))}-{str(item.pop())}")
    printnum = ", ".join(printlist)
    return(printnum)
    
def resolve(fromto = None):
    if fromto != None:
        fromtolist = fromto.split("-")
        fromnum = int(fromtolist.pop(0))
        tonum = int(fromtolist.pop()) + 1
        result = [a for a in range(fromnum, tonum)]
        return(result)
    return(None)
