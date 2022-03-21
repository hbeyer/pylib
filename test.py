#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
#from lib import xmlserializer as xs
#from lib import xmlreader as xr
#from lib import pica
logging.basicConfig(level=logging.INFO)

"""
def get_norm_p(pages, rule):
    normPages = 0
    if rule == "rda":
        extract = re.findall(r"(\d+) (ungezählte )?Seiten", pages)
        for group in extract:
            normPages += int(group[0])
        extract = re.findall(r"(\d+) (ungezählte |ungezähltes )?Bl[äa]tt", pages)
        for group in extract:
            normPages += int(group[0])*2
        extract = re.findall(r"(\d+) B[oö]gen", pages)
        for group in extract:
            normPages += int(group)*2                
        return(True)
    else:
        extract = re.findall(r"(\d+) S\.?", pages)
        for group in extract:
            normPages += int(group)
        extract = re.findall(r"\[?(\d+)\]? Bl\.?", pages)
        for group in extract:
            normPages += int(group)*2
    return(normPages)
"""

def get_norm_p(pages, rule = "rak"):
    normp = 0
    chunks = re.findall(r"(([^BS]+) (Bl)|([^BS]+) (S))", pages)
    for ch in chunks:
        _wh, numbl, _bl, nums, _s = ch
        if numbl != "":
            extrbl = re.findall(r"\d+", numbl)
            for num in extrbl:
                normp += int(num)*2
        elif nums != "":
            extrs = re.findall(r"\d+", nums)
            for num in extrs:
                normp += int(num)
    return(normp)
test = get_norm_p("40 ungezählte Blätter, 50, 60 Seiten")
print(test)
