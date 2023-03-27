#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import json
import re
from lib import gnd
from lib import cache
import urllib.request as ur

class Graph:
    def __init__(self, nodes = None, relations = None):
        self.nodes = []
        self.relations = []
        if nodes != None:
            for node in nodes:
                if isinstance(node, Node):
                    self.nodes.append(node)
                else:
                    logging.error("Ungültiger Knoten übergeben")                    
        if relations != None:
            for rel in relations:
                if isinstance(rel, Relation):
                    self.relations.append(rel)
                else:
                    logging.error("Ungültige Relation übergeben")
    def __str__(self):
        return(f"Graph mit {str(len(self.nodes))} Knoten und {str(len(self.relations))} Relationen")

class Node:
    def __init__(self, id = None, name = None, type = None, attributes = None):
        self.id = ""
        if isinstance(id, str):
            self.id = id
        self.name = ""
        if isinstance(name, str):
            self.name = name
        self.type = ""
        if isinstance(type, str):
            self.type = type
        self.attributes = {}
        if isinstance(attributes, dict):
            self.attributes = attributes
    def __str__(self):
        ret = f"{self.type}: {self.name}#{self.id}"
        return(ret)
        
class Relation:
    def __init__(self, origin = None, target = None, type = None, attributes = None):
        self.origin = None
        self.target = None
        if isinstance(origin, Node):
            self.origin = origin
        if isinstance(target, Node):
            self.target = target
        self.type = ""
        if isinstance(type, str):
            self.type = type
        self.attributes = {}
        if isinstance(attributes, dict):
            self.attributes = attributes
            
class GraphGND(Graph):
    def __init__(self):
        super().__init__()
        self.cache = cache.CacheGND()
        self.ids = set()
        self.ids_done = set()
    def importGNDs(self, gnds, type = None):
        type_node = "Person"
        if type != None:
            type_node = type
        for gndid in gnds:
            pers = gnd.Person(gndid, self.cache)
            node = self.make_node(pers, type_node)
            if node.id not in self.ids:
                self.nodes.append(node)
                self.ids.add(node.id)
    def make_node(self, person, type):
        node = Node(person.id, person.name, type, { "date_birth" : person.date_birth, "date_death" : person.date_death, "place_birth" : person.place_birth, "place_death" : person.place_death, "gender" : person.gender })
        return(node)
    def import_related(self):
        todo = self.ids.difference(self.ids_done)
        for gndid in todo:
            pers = gnd.Person(gndid, self.cache)
            idd_rel = [rel["id"] for rel in pers.relations]
            self.importGNDs(idd_rel)
            for rel in pers.relations:
                relation = Relation(pers.id, rel["id"], rel["type"])
                self.relations.append(relation)
            self.ids_done.add(pers.id)