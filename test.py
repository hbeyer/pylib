#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import roman
import zipfile
import os
from lib import sru
from lib import isil
from lib import recordlist as rl
from lib import xmlreader as xr
from lib import pica
from lib import csvt
from lib import romnumbers as rn
logging.basicConfig(level=logging.INFO)

"""
test = "M. C. LVIII"
print(test)
num = rn.to_arabic(test)
print(num)
rom = rn.to_roman(num)
print(rom)
"""

source_folder = f"downloads/helmstedt"

"""
req = sru.Request_VD17()
num = req.prepare("pica.bbg=(Aa* or Af* or Av*)")
print(req.url)
print(req.numFound)
req.download("source_folder")
"""

reader = xr.DownloadReader(source_folder, "record", "info:srw/schema/5/picaXML-v1.0")

for count, node in enumerate(reader):
    rec = pica.Record(node)
    for cp in rec.copies:
        print(cp.isil)
    if count >= 50:
            break
