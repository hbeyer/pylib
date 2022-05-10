#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import re
from lib import table_winibw as tw

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

expr_umf = r"\(?\d+\)? (Bll\.|S\.)"
expr_form = r"([248]|12)°"

nost = tw.Table("source/Angebotsliste-Nostitz.csv")

for count, row in enumerate(nost):
    umf = ""
    for tup, val in row.items():
        extr = re.search(expr_umf, val)
        if extr != None:
            umf = extr.group(0)
            break
    form = ""
    for tup, val in row.items():
        extr = re.search(expr_form, val)
        if extr != None:
            form = extr.group(0)
            break
    if umf != "" and form != "":
        koll = f"{umf}, {form}"
    elif umf != "":
        koll = umf
    elif form != "":
        koll = form
    else:
        koll = ""
    print(koll)
    
