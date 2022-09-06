#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import mysql.connector as mc
from lib import portapp as pa

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

new = pa.Artwork()
new.anumber = "B 1"
new.inventorynumber = "13-geom-00001"

db = mc.connect(user="root", password="allpaka", host="mysql", database="portraitdb")

new.insertIntoDB(db)
