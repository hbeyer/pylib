#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import pica
from lib import xmlreader as xr
from lib import csvt
from lib import geo
from lib import isil
from lib import language as lang

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

"""
test = "[13] Bl., S. 1-26, [1] gef. Bl. = S. 27/28, S. 29-148 [i.e.154], [2] gef. Bl. = S. 155/156, 157/158, S. 159-274, [1] gef. Bl. = S. 275/276, S. 277-312, [1] gef. Bl. = S. 313/314, S. 315-340, [1] gef. Bl. = S. 341/342, S. 343-370, [1] gef. Bl. = S. 371/372, S. 373-418, [1] gef. Bl. S. = 419/420, S. 421-436, [1] gef. Bl. = S. 437/438, S. 439-452, [2] gef. Bl. = S. 453/454, 455/456, S. 457-500, [1] gef. Bl. = S. 502[i.e.501]/502, S. 503-530, [9] Bl."
np = pica.get_norm_p(test)
print(str(np))
"""

reader = xr.SRUDownloadReader("../../Temporäres/2022-05-03_VD17-komplett")
tab = csvt.Table(["VD17", "Kollationsvermerk", "Normierte_Seiten"])

for count, node in enumerate(reader):
        rec = pica.RecordVD17(node)
        if rec.normPages > 2000 or len(rec.pages) > 100 or "Sp" in rec.pages:
            tab.content.append([rec.vdn, rec.pages, rec.normPages])
        if count > 5000:
            break
tab.save("Test-Kollation")
