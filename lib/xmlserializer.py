#!/usr/bin/python3
# -*- coding: utf-8 -*-

#import glob
#import urllib.request as ul
import xml.etree.ElementTree as et
#import re

class Serializer():
    def __init__(self, path, root = "root"):
        self.path = path + ".xml"
        self.root = et.Element(root)
        self.tree = et.ElementTree(self.root)
    def add_node(self, node):
        self.root.append(node)
        return(True)
    def add_nested(self, tag, content):
        node = make_node(tag)
        for key in content:
            subnode = make_node(key, content[key])
            node = add_subnode(node, subnode)
        self.add_node(node)
        return(True)
    def save(self):
        self.tree.write(self.path, encoding="UTF-8", \
                        xml_declaration=True, \
                        default_namespace=None, \
                        method="xml")
        return(True)
    def to_string(self):
        xml = et.tostring(self.root, encoding='utf8', xml_declaration=False)
        return(xml.decode('UTF-8'))
def add_subnode(node, subnode):
    node.append(subnode)
    return(node)
def make_node(name, value = None, att_name = None, att_value = None):
    el = et.Element(name)
    if value != None:
        el.text = value
    if att_name != None and att_value != None:
        el.set(att_name, att_value)
    return(el)
