#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ul
import re

class Grabber:
    def __init__(self, url):
        self.cache = cache
        self.url = url
        fileobject = ul.urlopen(self.url)
        self.response = ""
        try:
            self.response = fileobject.read().decode('utf-8')
        except:
            print("Keine Antwort von " + self.url)
    def getSnippets(self, regex, groups = [1]):
        mo = re.search(rf"{regex}", self.response, re.IGNORECASE)
        ret = []
        for gr in groups:
            if mo.group(gr):
                ret.append(mo.group(gr))
        return(ret)