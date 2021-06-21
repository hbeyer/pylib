#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import lido
from lib import xmlreader as xr

reader = xr.OAIDownloadReader("source/vkk")
for node in reader:
	rec = lido.Record(node)
	print(rec.image)