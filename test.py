#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lib import oai
import urllib.request as ur
import xml.etree.ElementTree as et

fo = ur.urlopen("http://oai.hab.de/?verb=ListRecords&metadataPrefix=mods")
tree = et.parse(fo)
tree.write("test.xml", "utf-8", True)

"""
req = oai.Request_OAI()
#req.id = "oai:diglib.hab.de:ppn_092253059"
req.download("testOAI", "oai_dc")
"""
