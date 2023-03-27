#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
from lib import network as nw
from lib import gnd
from lib import cache
from lib import network as nw
logging.basicConfig(level=logging.INFO)

"""
node1 = nw.Node("pers1", "Hartmut Beyer", "Person")
node2 = nw.Node("pers2", "Katrin Beyer", "Person")
rel = nw.Relation(node1, node2, "marriedTo", {"date" : "2010-08-21"})
graph = nw.Graph([node1, node2], [rel])
for node in graph.nodes:
    print(node)
print(graph)
"""

"""
ca = cache.Cache()
url = "http://d-nb.info/gnd/115513205/about/lds"
gnd = "115513205"
file = ca.get_content(url, gnd)
print(file)
"""

"""
ca = cache.CacheGND()
json = ca.get_json("11852190X")
print(json)
"""

graphgnd = nw.GraphGND()
graphgnd.importGNDs(["116118547"])
graphgnd.import_related()
graphgnd.import_related()
graphgnd.import_related()
print(graphgnd)
