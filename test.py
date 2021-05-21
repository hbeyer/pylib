#!/usr/bin/python3
# -*- coding: utf-8 -*-


#from lib import table_winibw as tw
from lib import csvt
from lib import geo
#from lib import shelfmark as sm

"""
table = csvt.Table(["placeName", "getty", "gnd", "long", "lat"], [["Frankfurt am Main", "7005293", "4018118-2", "", ""], ["Frankfurt (Oder)", "7005972", "4018122-4", "", ""], ["Dresden", "7004455", "4012995-0", "", ""], ["München", "7134068", "4127793-4", "", ""]])
table.save("placeData")
"""

"""
table.load("placeData")
print(table.fields)
"""

geo = geo.GeoDB("placeData.csv")
geo.addPlace("Berlin", "7209905", "4005728-8")
print(geo.table.content)
geo.save()