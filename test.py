#!/usr/bin/python3
# -*- coding: utf-8 -*-


from lib import table_winibw as tw
from lib import csvt

table = tw.Table("source/luther-buecherrad.csv")
sel = [[dict['Frequenz'], dict['Jahr']] for dict in table.content]
res = {}
for row in sel:
	try:
		res[row[1]] += int(row[0])
	except:
		res[row[1]] = int(row[0])
table = csvt.Table(['year', 'occurrences'], [[key, res[key]] for key in res])
table.save('erwerbung-buecherrad')