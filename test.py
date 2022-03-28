#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import geo

logging.basicConfig(level=logging.INFO)

from lib import geo

db = geo.DB()
test = db.get_by_name("Neustadt an der Aisch")
print(test)
