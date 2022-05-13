#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
import re
from lib import csvt
from lib import geo

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

gdb = geo.DB()
gdb.get_geodata()
gdb.save()


"""
testRow = csvt.GeoDataRow("Leipzig", "12.4167", "51.3333", "1650", 7)
testRow2 = csvt.GeoDataRow("Dresden", "13.7500", "51.0500", "1670", 5)
testRow3 = csvt.GeoDataRow("Leipzig", "12.4167", "51.3333", "1650", 20)
testRow4 = csvt.GeoDataRow("Pirna", "", "", "1700", 3)
gt = csvt.TableGeoBrowser([testRow, testRow2, testRow3, testRow4])
gt.simplify_content()
gt.fill_geo_data(gdb)
gt.save("testGeo")
"""