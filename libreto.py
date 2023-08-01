#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import sru
from lib import xmlserializer as xs
from lib import xmlreader as xr
from lib import pica
logging.basicConfig(level=logging.INFO)

req = sru.Request_HAB()
req.prepare("pica.prn=Elisabeth Sophie and pica.bbg=A[af]*")
print(f"Datensätze: {req.numFound}")
req.download("downloads/esm")

reader = xr.downloadReader("downloads/esm", "record", "info:srw/schema/5/picaXML-v1.0")

ser = xs.Serializer("esm-opac", "collection")
ser.add_nested("metadata", {
    "heading" : "Provenienz Elisabeth Marie Sophie",
    "description" : "Titel aus dem Vorbesitz der Herzogin Elisabeth Sophie Marie im OPAC der HAB",
    "owner" : "Elisabeth Marie Sophie",
    "ownerGND" : "104277122",
    "year" : "1767",
    "creatorReconstruction" : "Hartmut Beyer",
    "yearReconstruction" : "2022",
    "fileName" : "esm-opac"    
    })
for count, node in enumerate(reader):
    rec = pica.Record(node)
    itemNode = rec.toLibreto("Elisabeth")
    ser.add_node(itemNode)
    #if count > 100:
    #    break
ser.save()
