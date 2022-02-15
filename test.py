#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import geo
from lib import csvt
import logging
logging.basicConfig(level=logging.INFO)

#test = geo.getGettyLabel("7012821")
tbl = csvt.Table()
tbl.load("source/pcp-geo")
res = csvt.Table(["Ort_PCP", "Ort_Getty", "long", "lat", "GettyID"], [])
for row in tbl.content:
    label, _a, _b, long, lat, _c, _d, _e, getty = row
    labelGetty = ""
    if getty != "":
        labelGetty = geo.getGettyLabel(getty)
    res.content.append([label, str(labelGetty), long, lat, "http://vocab.getty.edu/page/tgn/7106209" + getty])
    print(str(labelGetty))
res.save("pcp-geodata")
