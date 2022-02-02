#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import geo
from lib import csvt
import logging
logging.basicConfig(level=logging.INFO)

result = csvt.Table(["label", "getty", "long", "lat"], [])

ga = geo.DB()
tbl = csvt.Table()
tbl.load("source/Places_PCP", "cp1252")
for row in tbl.content:
    name = row[1].strip()
    test = ga.getByName(name)
    try:
        blabel, bgetty, _gnd, blong, blat, _x =  test
    except:
        result.content.append([name, "", "", ""])
    else:
        result.content.append([name, bgetty, blong, blat])
result.save("PCP-Geodata")

"""
gb_fields = ["Name", "Address", "Description", "Longitude", "Latitude", "TimeStamp", "TimeSpan:begin", "TimeSpan:end", "GettyID"]

table_birth = csvt.Table(gb_fields, [])
table_chair = csvt.Table(gb_fields, [])

ga = geo.DB()

for row in tbl.content:
    _url, lecturer, birth_year, birth_place, chair_year, chair_place = row
    if birth_year:
        birth_year += "-01-01"
    if chair_year:
        chair_year += "-01-01"        
    birth_row = ga.getByName(birth_place)
    if birth_row != False:
        blabel, bgetty, _gnd, blong, blat, _x =  birth_row
        table_birth.content.append([birth_place, f"Geburtsort {lecturer}", "", blong, blat, birth_year, "", "", bgetty])
    else:
        table_birth.content.append([birth_place, f"Geburtsort {lecturer}", "", "", "", birth_year, "", "", ""])
    chair_row = ga.getByName(chair_place)
    if chair_row != False:
        clabel, cgetty, _gnd, clong, clat, _x = chair_row
        table_chair.content.append([chair_place, f"Lehrstuhl {lecturer}", "", clong, clat, chair_year, "", "", cgetty])
    else:
        table_chair.content.append([chair_place, f"Lehrstuhl {lecturer}", "", "", "", chair_year, "", "", ""])
table_birth.save("pcp-geburtsorte")
table_chair.save("pcp-lehrstuhlorte")

table_all = csvt.Table(gb_fields, table_birth.content + table_chair.content)
table_all.save("pcp-alle_orte")
"""
