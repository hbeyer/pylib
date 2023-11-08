#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import json
import re
from lib import gnd
from lib import cache
import urllib.request as ur
from neo4j import GraphDatabase
import io

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
    def to_cypher(self):
        commands = []
        for node in self.nodes:
            node.attributes["name"] = node.name
            node.attributes["given_id"] = node.id
            attributes = print_properties(node.attributes)
            commands.append(f"MERGE (n:{node.type} {attributes})")
        for rel in self.relations:
            type = encode_cypher(rel.type)
            attributes = print_properties(rel.attributes)
            commands.append(f"MATCH (a), (b) WHERE a.given_id = '{rel.origin}' AND b.given_id = '{rel.target}' MERGE (a)-[r:{type}{' ' + attributes if attributes != '' else ''}]->(b)")
        return(commands)
    def to_neo4j(self, uri, user, pw, db, clear = True):           
        driver = GraphDatabase.driver(uri, auth=(user, pw))
        driver.verify_connectivity()
        if clear == True:
            with driver.session(database=db) as session:
                session.execute_write(run_cypher, "MATCH (n)-[r]->(m) DELETE r")
                session.execute_write(run_cypher, "MATCH (n) DELETE n")
                logging.info(f"Datenbank geleert")
        commands = self.to_cypher()
        with driver.session(database=db) as session:
            for count, command in enumerate(commands):  
                session.execute_write(run_cypher, command)
                #logging.info(f"Ausgeführt: {command}")
                if count > 300000:
                    break
        driver.close()
    def save_cypher(self, file_name = None):
        path = "graph.cypher"
        if file_name != None:
            path = f"{file_name}.cypher"
        content = self.to_cypher()
        content = ";\n".join(content)
        save_file(path, content)
    def __str__(self):
        return(f"Graph mit {str(len(self.nodes))} Knoten und {str(len(self.relations))} Relationen")

class Node:
    def __init__(self, id = None, name = None, type = None, attributes = None):
        self.id = ""
        if id != None:
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
        # Hier ist ein Problem!
        self.origin = ""
        self.target = ""
        if origin != None:
            self.origin = origin
        if target != None:
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
            pers = gnd.Person(str(gndid), self.cache)
            node = self.make_node(pers, type_node)
            if str(node.id) not in self.ids:
                self.nodes.append(node)
                self.ids.add(str(node.id))
    def make_node(self, person, type):
        node = Node(person.id, person.name, type, { "date_birth" : person.date_birth, "year_birth" : person.year_birth, "date_death" : person.date_death, "year_death" : person.year_death, "place_birth" : person.place_birth, "place_death" : person.place_death, "gender" : person.gender })
        return(node)
    def import_node(self, node):
        if isinstance(node, Node) != True:
            print(f"Kein Node übergeben: {str(node)}")
            return(False)
        if str(node.id) in self.ids:
            return(False)
        self.nodes.append(node)
        self.ids.add(str(node.id))
        return(True)
    def import_related(self):
        todo = self.ids.difference(self.ids_done)
        for gndid in todo:
            if gnd.ID(gndid).valid != True:
                self.ids_done.add(str(gndid))
                continue
            pers = gnd.Person(str(gndid), self.cache)
            idd_rel = [rel["id"] for rel in pers.relations]
            self.importGNDs(idd_rel)
            for rel in pers.relations:
                relation = Relation(gndid, rel["id"], rel["type"])
                self.relations.append(relation)
            self.ids_done.add(str(pers.id))
          
def print_properties(propp):
    if isinstance(propp, dict) != True or propp == {}:
        return("")
    elements = []
    for key, val in propp.items():
        val = val.replace("'", "ʼ")
        elements.append(f"{key} : '{val}'")
    return("{" + ", ".join(elements) + "}")
    
def encode_cypher(text):
    conc = { 
        "VD-16 Mitverf." : "VD16Mitverf",
        "1. Ehefrau" : "ersteEhefrau" ,
        "2. Ehefrau" : "zweiteEhefrau",
        "3. Ehefrau" : "dritteEhefrau",
        "1. Ehemann" : "ersterEhemann",
        "2. Ehemann" : "zweiterEhemann",
        "3. Ehemann" : "dritterEhemann"
        }
    try:
        text = conc[text]
    except:
        pass
    text = text.replace("-", "").replace(".", "").replace(" ", "").replace(",", "").replace(";", "").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss").replace("[?]", "_fragl").replace("?", "_fragl").replace("(", "").replace(")", "").replace("[", "_").replace("]", "")
    if re.match("^[0-9].+", text):
        text = f"No{text}"
    return(text)
          
def save_file(path, content):
    with io.open(path, 'w', encoding='utf8') as f:
        f.write(content)
    logging.info(f"Datei gespeichert unter {path}")
    return(True)
    
def run_cypher(tx, command):
    result = tx.run(command)
    record = result.single()
    return(record)