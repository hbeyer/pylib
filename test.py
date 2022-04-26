#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from lib import duennhaupt as dh
from lib import evalpdf as ep
from lib import csvt

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

qww = dh.get_query_words()

ev = ep.Evaluation("source/kataloge/HH_A151.pdf", qww)
ev.eval()
print(ev)
