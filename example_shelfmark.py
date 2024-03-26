#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
from lib import sru
from lib import xmlreader as xr
from lib import pica
from lib import csvt
from lib import shelfmark as sm
logging.basicConfig(level=logging.ERROR)

# Festlegen eines Downloadordners und eines Limits für den Testbetrieb
download_folder = f"downloads/opac"
limit = 1000

# Download aller Druckschriften mit Erscheinungsjahr 1670 aus dem OPAC
"""
req = sru.Request_HAB()
num = req.prepare("pica.jah=1670 and pica.bbg=(Aa* or Af*)")
#num = req.prepare("pica.tit=dissertatio")
print(req.url)
print(f"{req.numFound} Treffer")
req.download(download_folder)
"""


"""
reader = xr.DownloadReader(download_folder,"record", "info:srw/schema/5/picaXML-v1.0")#
records = list([pica.Record(node) for count, node in enumerate(reader) if count < limit])
shelfmarks = set()
for rec in records:
    for cop in rec.copies:
        shelfmarks.add(cop.sm)
"""

shelfmarks = ['H: T 729a.2° Helmst. ', 'M: Ho 298 (4)', 'Lpr. Stolb. 19280 (2) ', 'Xb 4558', 'Textb. 481', 'M: Gn Kapsel 52 (6)', 'M: Li 4611', 'M: Da 602 (12)', 'Xb 10102', 'GE 58-3855', 'M: QuN 1041 (1)', 'M: Cd 4° 84 (7)', 'M: Jb 93', 'M: Be Kapsel 3 (28)', 'M: Gg 141', 'M: Da 593 (4)', 'Xb 2806 (54)', 'M: Mk 292', 'Xb 12° 388', 'M: Gm 4° 1066 (26)', 'A: 738.14 Theol.', 'H: 521 Helmst. Dr. (79)', 'Schulenb. Gb 10', 'H: P 535.2° Helmst. (1)', 'M: QuN 949 (5)', 'Xb 2806 (17)', 'Xb 2806 (43)', 'M: Ro 2° 2', 'Xb 5128', 'A: 260.16 Quod. (12)', 'M: Rh 4° 35', 'M: Lg 1844', 'Xb 12° 359', 'H: Yv 861.8° Helmst.', 'M: Th 903:2 (2)', 'M: QuN 953 (2)', 'H: B 7.4° Helmst. (8)']

struct_smm = { sm.StructuredShelfmark(shelfmark).sortable : shelfmark for shelfmark in shelfmarks }

index = sorted(struct_smm)

for ind in index:
    print(f"{struct_smm[ind]} - {ind}")

"""
for sort, sm in struct_smm.items():
    print(f"{sm} - {sort}")
"""


