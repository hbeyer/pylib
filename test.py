#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from lib import duennhaupt as dh
from lib import evalpdf as ep
from lib import table_winibw as tw
from lib import shelfmark as sm

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

"""
sigg = ["Wa 2° 75:1", "Xb 2385", "Wa 6897", "Xb 10462"]
for sig in sigg:
    ssig = sm.StructuredShelfmark(sig)
    sort = ssig.sortable
    print(f"{sig} - {ssig} - {sort}")
"""

tb = tw.Table("source/portraitsammelwerke_digi.csv")
tb.addSortable()
tb.save("Checkliste_Porträtsammelwerke")
