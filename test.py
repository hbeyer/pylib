#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import sru
folder = "downloads"
req = sru.Request_HAB()
req.prepare("pica.prn=Baudis and pica.bbg=A[af]*")
print(f"Datensätze: {req.numFound}")
req.download(folder)
