#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import roman
import zipfile
import os
from lib import sru
from lib import isil
from lib import recordlist as rl
from lib import xmlreader as xr
from lib import pica
from lib import csvt
logging.basicConfig(level=logging.INFO)

source_folder = f"../../Temporäres/2022-03-04_VD17-komplett/"
#download_folder = f"../vd17-dump/"

"""
test = "MDC i.e. 101 Seiten"
norm = pica.get_norm_p(test)
print(str(norm))
"""

"""
req = sru.Request_VD17()
num = req.prepare("pica.bbg=(Aa* or Af* or Av*)")
print(req.url)
print(req.numFound)
req.download("source_folder")
"""

reader = xr.DownloadReader(source_folder, "record", "info:srw/schema/5/picaXML-v1.0")

res = csvt.Table(["VDN", "Kollation", "Normiert"], [])

for count, node in enumerate(reader):
    rec = pica.RecordVD17(node)
    if len(rec.pages) > 20:
        res.content.append([rec.vdn, rec.pages, rec.normPages])
    if count > 1000:
        break

res.save("Seitennormierung_VD17")
