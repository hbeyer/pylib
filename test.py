#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import xmlreader as xr

reader = xr.SRUDownloadReader("source/vd17")
for node in reader:
	print(node)
