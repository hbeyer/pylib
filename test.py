#!/usr/bin/python3
# -*- coding: utf-8 -*-


#from lib import table_winibw as tw
from lib import csvt
from lib import geo
#from lib import shelfmark as sm

#test = geo.getGeoDataGND("4057260-2")
#print(test)

"""
isill = set()
reader = pica.downloadReader("../../Temporäres/2021-05-05_VD17-komplett")
#reader = pica.downloadReader("source/vd17")
for node in reader:
	rec = pica.Record(node)
	isill.add(rec.isilRec)
for il in isill:
	print(il)
"""

db = geo.DB()
db.getGeoData()
db.save()
