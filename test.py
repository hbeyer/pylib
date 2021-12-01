#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import dspace as ds
from lib import dataset as dts

import logging
logging.basicConfig(level=logging.INFO)

dset = dts.DatasetDC()
ety = dts.Entry("G. Julius Caesar", None, "GND", "118518275")
dset.addEntry("contributor", ety)
print(dset.toList())
