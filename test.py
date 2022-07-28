#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import pica
from lib import xmlreader as xr
from lib import csvt
from lib import geo
from lib import isil
from lib import language as lang
from lib import duennhaupt as dh

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

perss = dh.get_persons()
print(perss[3])

"""
reader = xr.SRUDownloadReader("../../Temporäres/2022-05-03_VD17-komplett")
limit = 350000
tbl = csvt.Table(["VD17", "Titel", "Ort", "Jahr", "Seiten", "Normseiten", "Gattung", "Exemplare"])


for count, node in enumerate(reader):
        rec = pica.RecordVD17(node)
        if rec.normPages > 2 or rec.normPages == 0:
                continue
        for gat in rec.gatt:
                if "Dissertation" in gat:
                        tbl.content.append([rec.vdn, rec.title, ", ".join([pl.placeName for pl in rec.places]), rec.date, rec.pages, rec.normPages, gat, str(len(rec.copies))])
                        break
        if count > limit:
                break
tbl.save("VD17-Dissertationen_1-2")
"""
