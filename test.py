#!/usr/bin/python3
# -*- coding: utf-8 -*-


from lib import table_winibw as tw
from lib import csvt
from lib import shelfmark as sm

"""
test = "M: Li 5530 Slg. Hardt (57, 1147)"
sig = sm.StructuredShelfmark(test)
print(sig)
"""

table = tw.Table("source/Luther_Mittlere.csv")
table.filter(lambda row: row if row["Signatur"][0:2] == "M:" else None)
table.filter(lambda row: row if row["Jahr"][0:2] == "17" else None)
sigg = table.getByField("Signatur")
smList = sm.ShelfmarkList([sm.StructuredShelfmark(sig) for sig in sigg])
smList.makeVolumes()
for vol in smList:
	print(vol)
"""
table.addSortable()
table.addParallels()
table.save("Luther_Mittlere-bearb")
"""