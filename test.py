#!/usr/bin/python3
# -*- coding: utf-8 -*-


#from lib import table_winibw as tw
from lib import csvt
from lib import geo
#from lib import shelfmark as sm

#test = geo.getGeoDataGND("4057260-2")
#print(test)


db = geo.DB()
db.getGeoData()
db.save()
