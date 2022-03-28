#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import geo

logging.basicConfig(level=logging.INFO)

from lib import bookwheel as bw
cat = bw.Catalogue
sec = cat.get_section(2589)
print(sec)
