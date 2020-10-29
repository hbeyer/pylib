#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import opac

grab = opac.grabber("per beyer and tit drama")
print(str(grab.numFound))
#xml = grab.getXML()
#print(xml)
