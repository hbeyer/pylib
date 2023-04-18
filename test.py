#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import gesa
logging.basicConfig(level=logging.INFO)

req = gesa.MultRequest("1600-1700", 3960)
req.grab_data(120000)
req.to_csv()
