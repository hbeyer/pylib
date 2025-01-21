#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import urllib.parse as up
from lib import sru
from lib import pica
from lib import xmlreader as xr

class Evaluation:
    def __init__(self, pers = None, title = None, place = None, year = None):
        query_ell = []
        if pers != None:
            query_ell.append(f"pica.per={pers}")
        if title != None:
            words = get_words(clean_title(title))
            query_ell.append(f"pica.tit={'+'.join(words)}")
        if place != None:
            query_ell.append(f"pica.vlo={place}")
        if year != None:
            query_ell.append(f"pica.jah={year}") 
        self.query = " and ".join(query_ell)
        self.req = sru.Request_K10plus()
        self.numFound = 0
        self.ppns = []
        self.shelfmarks = []
    def evaluate(self):
        self.req.prepare(self.query)
        self.numFound = self.req.numFound
        if self.numFound == 0:
            return(0)
        reader = xr.WebReader(self.req.url, "record", "info:srw/schema/5/picaXML-v1.0")
        for node in reader:
            rec = pica.Record(node)
            if re.search("A[baFf][uv]", rec.bbg[0:3]) != None:
                self.ppns.append(rec.ppn)
                self.shelfmarks.extend([cp.sm for cp in rec.copies])
        if len(self.ppns) == 0:
            for node in reader:
                rec = pica.Record(node)
                if re.search("A[baFf]", rec.bbg[0:2]) != None:
                    self.ppns.append(rec.ppn)
                    self.shelfmarks.extend([cp.sm for cp in rec.copies])
        return(self.numFound)

class Evaluation_HAB(Evaluation):
    def __init__(self, pers = None, title = None, place = None, year = None):
        super().__init__(pers, title, place, year)
        self.req = sru.Request_HAB()
        
def clean_title(title):
    title = title.split("\n").pop(0)
    repl = {
        "\n" : " ",
        "." : "",
        "," : "",
        "\"" : "",
        "(" : "",
        ")" : ""
        }
    for key, val in repl.items():
        title = title.replace(key, val)
    return(title)

def get_words(title, count = None, stop_words = None):
    if count == None:
        count = 5
    title = title.lower()
    title = clean_title(title)
    words = title.split(" ")
    if stop_words == None:
        stop_words = ["der", "die", "das", "eine", "ein", "von", "vom", "the", "of", "og", \
                  "le", "la", "à", "les", "ou", "il", "a", "in", "im",  "del", "di", "col", \
                  "o", "vom", "dem", "de", "du", "des", "et", "e", "ed", "und", "an", "and", \
                  "or", "with", "on", "at", "sur", "s", "l", "en", "+", "ä", "y", "zu", "den", "d", \
                  "&", "—", "t", "zur", "zum", "het", "s", "für", "i"]
    words = list(filter(lambda w: None if w in stop_words else w, words))
    words = list(filter(lambda w: None if len(w) == 1 else w, words))
    words = list(filter(lambda w: None if re.search("\d", w) is not None else w, words))
    ret = []
    while len(ret) < count and len(words) > 0:
        ret.append(words.pop(0))
    return(list(ret))