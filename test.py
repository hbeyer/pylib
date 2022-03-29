#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import dataset as ds

example = ds.DatasetDC()
example.add_entry("dc.identifier", ds.Entry("VD16 D 340"))
example.add_entry("dc.title", ds.Entry("Poematum || HENRICI || DECIMATORIS || GIFFHORNENSIS.|| Libri IIII.||", "lat"))
example.add_entry("dc.creator", ds.Entry("Decimator, Heinrich", "", "GND", "124613934"))
example.add_entry("dc.date", ds.Entry("1586"))

print(example.to_dict())
