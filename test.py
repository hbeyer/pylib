#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import table_winibw as tw
from lib import shelfmark as sm

table = tw.Table("augusteer-luther.csv")
table.filter(lambda x : (x if x["Signatur"][0:3] == "A: " else None))
result = [sm.searchable(sm.SortableShelfmark(row["Signatur"]).whole) for row in table.content if sm.SortableShelfmark(row["Signatur"]).number.find(".") == -1]
print("|".join(result))