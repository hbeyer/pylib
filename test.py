#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import xmlserializer as xs
from lib import xmlreader as xr
from lib import pica
logging.basicConfig(level=logging.INFO)

reader = xr.downloadReader("downloads/esm", "record", "info:srw/schema/5/picaXML-v1.0")

ser = xs.Serializer("testSer", "collection")
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
    logging.info(rec.vdn)
    itemNode = rec.toLibreto("Elisabeth")
    ser.add_node(itemNode)
    if count > 100:
        break
ser.save()