#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import mysql.connector as mc
from lib import portapp as pa

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

db = mc.connect(user="root", password="allpaka", host="mysql", database="portraitdb")

ac = pa.ArtCollection(db)
ac.loadByANumber("B 2", False)

try:
    ac.content[0].deleteFromDB(db)
except:
    logging.info("Nichts zu löschen")

"""
new = pa.Artwork()
new.anumber = "B 2"
new.inventorynumber = "13-geom-00002"
new.description = "<description><p>Kupferstich einer Porträtbüste. Aufschrift „Aeschines | (gr.:) AISCHINES | ATROMETOY | AXENAIOS | Apud magnum Etruriae Ducem in marmore.“</p></description>"
pers = pa.Person()
pers.gnd = "118637622"
pers.name = "Aeschines"
new.personsRepr.append(pers)

new.insertIntoDB(db)
"""