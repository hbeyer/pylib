#!/usr/bin/python3
# -*- coding: utf-8 -*-


import logging
from lib import duennhaupt as dh
from lib import evalpdf as ep

qww = dh.get_query_words()

ev = ep.Evaluation("source/kataloge/jeschke141.pdf", qww)
ev.eval()
print(ev)
