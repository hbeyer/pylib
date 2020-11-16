#!/usr/bin/python3
# -*- coding: utf-8 -*-

#from lib import bookwheel as bw
#eva = bw.EvaluationYear("pages-luther.txt")
#eva.save("luther")

from lib import mets

mb = mets.METSBuilder("33-6-aug-2f")
mb.build()