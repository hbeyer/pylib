#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ul
import re
import logging

class Grabber:
    def __init__(self, url):
        self.url = url
        fileobject = ul.urlopen(self.url)
        self.response = ""
        try:
            self.response = fileobject.read().decode('utf-8')
        except:
            print("Keine Antwort von " + self.url)
    def getSnippets(self, regex, groups = None):
        self.groups = [1]
        if groups != None:
            self.groups = groups
        mo = re.search(rf"{regex}", self.response, re.IGNORECASE)
        ret = []
        for gr in self.groups:
            try:
                ret.append(mo.group(gr))
            except:
                logging.error(f"Kein Treffer für group {gr}")
        return(ret)
