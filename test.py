#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import pickle
from lib import pica
from lib import xmlreader as xr
from lib import csvt
from lib import geo
from lib import isil
from lib import language as lang
from lib import duennhaupt as dh

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

with open('gattungen-ac','rb') as file:
    gatt_ac = pickle.load(file)

reader = xr.SRUDownloadReader("../../Temporäres/2022-05-03_VD17-komplett")
limit = 350000
tbl = csvt.Table(["VD17", "Titel", "Ort", "Jahr", "Seiten", "Normseiten", "Gattung", "Exemplare"])


for count, node in enumerate(reader):
        rec = pica.RecordVD17(node)
        if rec.get_rec_type() in ["Teilband", "Teilband mit eigenem Titel"]:
            try:
                rec.gatt = gatt_ac[rec.ppn_sup]
            except:
                logging.info(f"Ohne Gattungsbegriff: {rec.ppn}")         
        if rec.normPages > 1024 or rec.normPages < 513:
                continue
        if "Zeitung" in rec.gatt:
            tbl.content.append([rec.vdn, rec.title, ", ".join([pl.placeName for pl in rec.places]), rec.date, rec.pages, rec.normPages, ";".join(rec.gatt), str(len(rec.copies))])
        if count > limit:
                break
tbl.save("VD17-Zeitung_513-1024")
