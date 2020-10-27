#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as et
et.register_namespace("mets", "http://www.loc.gov/METS/")
et.register_namespace("mods", "http://www.loc.gov/mods/v3")
et.register_namespace("tei", "http://www.tei-c.org/ns/1.0")
et.register_namespace("dv", "http://www.dfg-viewer.de")
et.register_namespace("xlink", "http://www.w3.org/1999/xlink")
import urllib.request as ul

class METSBuilder:
        def __init__(self, sign, title="-"):
                self.title = title
                self.sign = sign
                self.url = "http://diglib.hab.de/mss/" + sign + "/start.htm"
                self.struct = []
                try:
                        fileobject = ul.urlopen(self.url)
                except:
                        print("Kein Digitalisat vorhanden unter " + self.url)
                else:
                        try:
                                facs = ul.urlopen("http://diglib.hab.de/mss/" + self.sign + "/facsimile.xml")
                        except:
                                print("Keine facsimile.xml vorhanden unter http://diglib.hab.de/mss/" + self.sign + "/facsimile.xml")
                                self.countPages()
                        else:
                                self.facs = facs
                                self.getStruct()

        def getStruct(self):
                tree = et.parse(self.facs)
                root = tree.getroot()
                nodes = root.findall('.//{http://www.tei-c.org/ns/1.0}graphic')
                for node in nodes:
                        try:
                                page = extractNumber(node.attrib["url"])
                        except:
                                return(None)
                        try:
                                label = node.attrib["n"]
                        except:
                                label = None
                        self.struct.append({ "page" : page, "label" : label })
        def countPages(self):
                i = 1
                while 1 == 1:
                        page = str(i).zfill(5)
                        url = "http://diglib.hab.de/mss/" + self.sign + "/min/" + page + ".jpg"
                        try:
                                fo = ul.urlopen(url)
                        except:
                                return(1)
                        else:
                                self.struct.append({ "page" : page, "label" : None })
                                i += 1
        def build(self):
                tree = et.parse('vorlage.xml')
                root = tree.getroot()
                titleEl = root.findall('.//{http://www.tei-c.org/ns/1.0}head/{http://www.tei-c.org/ns/1.0}title')
                try:
                        titleEl[0].text = self.title
                except:
                        print("Fehler beim Einfügen des Titels")
                items = root.findall('.//{http://www.dfg-viewer.de}presentation')
                try:
                        items[0].text = self.url
                except:
                        print("dv:presentation konnte nicht gesetzt werden.")
                fgg = root.findall('.//{http://www.loc.gov/METS/}fileGrp')
                for fg in fgg:
                        fg = appendFiles(fg, self.struct, self.sign)
                sm = root.findall('.//{http://www.loc.gov/METS/}div')
                for sm in sm:
                        if sm.attrib["TYPE"] == "physSequence":
                                count = 1
                                for struct in self.struct:
                                        divEl = et.SubElement(sm, "mets:div")
                                        divEl.set("ID", "PHYS_" + struct["page"])
                                        divEl.set("ORDER", str(count))
                                        count += 1
                                        divEl.set("TYPE", "page")
                                        if struct["label"] != None:
                                                divEl.set("ORDERLABEL", struct["label"])
                                        for use in ['DOWNLOAD', 'THUMBS', 'DEFAULT', 'MAX', 'MIN']:
                                                fptr = et.SubElement(divEl, "mets:fptr")
                                                fptr.set("FILEID", "FILE_" + struct["page"] + "_" + use)
                sl = root.findall('.//{http://www.loc.gov/METS/}structLink')
                for sl in sl:
                        for struct in self.struct:
                                smLink = et.SubElement(sl, "mets:smLink")
                                smLink.set("{http://www.w3.org/1999/xlink}from", "LOG_000")
                                smLink.set("{http://www.w3.org/1999/xlink}to", "PHYS_" + struct["page"])
                fileName = self.sign + "-mets.xml" 
                f = open(fileName, "w", -1, "utf_8")
                tree.write(f, encoding="unicode")
                return(1)

def appendFiles(fg, struct, sign):
        use = fg.attrib["USE"]
        concordance = { "DOWNLOAD" : "/download", "THUMBS" : "/thumbs", "DEFAULT" : "", "ORIGINAL" : "/max", "MAX" : "/max", "MIN" : "/min" }
        ending = ".jpg"
        if use == "DOWNLOAD":
                ending = ".pdf"
        for struct in struct:
                fileEl = et.SubElement(fg, "mets:file")
                fileEl.set("ID", "FILE_" + struct["page"] + "_" + use)
                if use == "DOWNLOAD":
                        fileEl.set("MIMETYPE", "application/pdf")
                else:
                        fileEl.set("MIMETYPE", "image/jpeg")
                if struct["page"] == "00001" and use != "DOWNLOAD":
                        fileEl.set("USE", "PREVIEW")
                flocatEl = et.SubElement(fileEl, "mets:FLocat")
                flocatEl.set("LOCTYPE", "URL")
                flocatEl.set("LOCTYPE", "URL")
                flocatEl.set("{http://www.w3.org/1999/xlink}href", "http://diglib.hab.de/mss/" + sign + concordance[use] + "/" + struct["page"] + ending)
        return(fg)

def extractNumber(number):
        no = re.findall("http://diglib.hab.de/mss/[^/]+/([0-9]+).jpg", number)
        return(no[0])
        
def removeLinebreaks(text, replacement=" "):
	text = text.replace("\n", replacement)
	text = text.replace("  ", " ")
	return(text)        