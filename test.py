#!/usr/bin/python3
# -*- coding: utf-8 -*-


from lib import table_winibw as tw
from lib import csvt

table = tw.Table("source/Luther_Helmst.csv")
table.filter(lambda row: row if row["Provenienz"] != "" else None)
table.filter(lambda row: row if row["Signatur"][0:2] == "H:" else None)
syn = {}
for row in table:
	parts = row["Provenienz"].split("; ")
	provv = [part.replace("|p|", "").replace("|k|", "") for part in parts if part != ""]
	for prov in provv:
		try:
			syn[prov.strip()].append(row["Signatur"])
		except:
			syn[prov.strip()] = [row["Signatur"]]
syntab = csvt.Table(["Provenienz", "Exemplare", "Suche"], [[name, ";".join(syn[name]), "|".join(syn[name]).replace("(", "").replace(")", "")] for name in syn])
syntab.save("Luther_Helmstedt_Prov")