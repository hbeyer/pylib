#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.request as ur
import re
import urllib.parse as up
import os.path as op
import xml.etree.ElementTree as et


class grabber:
    def __init__(self, query):
        self.query = query
        self.url = "http://opac.lbs-braunschweig.gbv.de/DB=2/XML=1.0/CMD?ACT=SRCHA&TRM=" + up.quote(self.query)
        self.response = ""
        self.numFound = 0
        try:
            self.response = ur.urlopen(self.url, None, 10).read().decode('utf-8')
        except:
            print("Keine Antwort von " + self.url)
        else:
            test = re.search(r"hits=\"([0-9]+)\"", self.response)
            try:
                self.numFound = int(test.group(1))
            except:
                print("Keine Trefferzahl bei " + self.url)
            else:
                if self.numFound > 500:
                    print("Zu viele Treffer (" + self.numFound + ")")
    def getXML(self):
        self.url = "http://opac.lbs-braunschweig.gbv.de/DB=2/XML=1.0/SHRTST=500/FULLTITLE=1/PRS=XML/XMLSAVE=N/CMD?ACT=SRCHA&IKT=1016&SRT=YOP&TRM=" + up.quote(self.query)
        try:
            self.response = ur.urlopen(self.url, None, 10).read().decode('utf-8')
        except:
            print("Keine Antwort von " + self.url)
            return(None)
        return(self.response)