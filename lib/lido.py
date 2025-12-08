#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import urllib.request as ul
import xml.etree.ElementTree as et

class Record:
    def __init__(self, node):
        self.ns = { "lido" : "{http://www.lido-schema.org}" }
        self.node = node
        self.persons = []
        self.date = ""
        self.isil = ""
        self.institution = ""
        self.dim_plate = (None, None)
        self.dim_sheet = (None, None)
        self.subjects = []
        self.iconclass = ""
        self.iconclass_notation = ""
        self.iconclass_labels = ""
        self.image = ""
        self.thumb = ""
        self.purl = ""
        self.comment = ""
        try:
            self.idRec = self.getFieldValues("lidoRecID").pop(0)
        except:
            self.idRec = ""
            print("Leere ID")
        try:
            self.id = self.idRec.split(":").pop(-1)
        except:
            self.id = ""
            print("ID nicht lesbar: " + self.idRec)
        try:
            self.title = ", ".join(self.getPathValues(".//" + self.ns["lido"] + "titleSet/" + self.ns["lido"] + "appellationValue"))
        except:
            self.title = ""
            print("Kein Titel (ID " + self.id + ")")
        if "\n" in self.title:
            self.title = self.title.replace("\n", "")
            self.title = self.title.replace("  ", " ")
        self.get_current_location()
        try:
            self.institution = {"DE-23" : "HAB", "DE-MUS-026819" : "HAUM"}[self.isil]
        except:
            self.institution = "[andere Institution]"
        self.cultures = self.getPathValues(".//" + self.ns["lido"] + "culture/" + self.ns["lido"] + "term")
        self.get_date()
        self.technique = self.getPathValues(".//" + self.ns["lido"] + "termMaterialsTech/" + self.ns["lido"] + "term")
        self.object_type = self.getPathValues(".//" + self.ns["lido"] + "objectWorkType/" + self.ns["lido"] + "term")
        self.getPersons()
        self.get_dimensions()
        self.get_subjects()
        self.getLinks()
    def getPersons(self):
        evnn = self.node.findall(".//" + self.ns["lido"] + "event")
        for en in evnn:
            try:
                evType = en.findall(".//" + self.ns["lido"] + "eventType/" + self.ns["lido"] + "term")[0]
            except:
                continue
            if evType.text == "Erschaffung/Herstellung":
                eaa = en.findall(".//" + self.ns["lido"] + "eventActor")
                for ea in eaa:
                    try:
                        name = ea.findall(".//" + self.ns["lido"] + "appellationValue")[0].text
                    except:
                        name = "?"
                    pers = Person(name)
                    try:
                        pers.role = ea.findall(".//" + self.ns["lido"] + "roleActor/" + self.ns["lido"] +  "term")[0].text
                    except:
                        pass
                    self.persons.append(pers)
    def get_current_location(self):
        ndd = self.node.findall(".//" + self.ns["lido"] + "repositorySet")
        for nd in ndd:
            rep_type = nd.get(self.ns["lido"] + "type")
            if rep_type == "current":
                self.isil = nd.find(self.ns["lido"] + "repositoryName/" + self.ns["lido"] + "legalBodyID").text
                self.shelfmark = nd.find(self.ns["lido"] + "workID").text
                break
    def get_date(self):
        event_nodes = self.node.findall(".//" + self.ns["lido"] + "event")
        for nd in event_nodes:
            event_type = nd.find(self.ns["lido"] + "eventType/" + self.ns["lido"] + "term").text
            if event_type.strip().lower().replace("/", "").replace(" ", "") == "erschaffungherstellung":
                try:
                    date_e = nd.find(self.ns["lido"] + "eventDate/" + self.ns["lido"] + "date/" + self.ns["lido"] + "earliestDate").text
                except:
                    date_e = None
                try:
                    date_l = nd.find(self.ns["lido"] + "eventDate/" + self.ns["lido"] + "date/" + self.ns["lido"] + "earliestDate").text
                except:
                    date_l = None
                if date_e and date_l:
                    self.date = date_e if date_e == date_l else f"{date_e}–{date_l}"
                    return(True)
                self.date_e if date_e else date_l if date_l else "s. a."
                return(True)
    def get_dimensions(self):
        measure_nodes = self.node.findall(".//" + self.ns["lido"] + "objectMeasurements")
        for mnd in measure_nodes:
            try:
                type = mnd.find(f"{self.ns['lido']}extentMeasurements").text
            except:
                self.comment = f"Unklare oder nicht vorhandene Maßangabe"
                type = "Blatt"
            dim_nodes = mnd.findall(self.ns["lido"] + "measurementsSet/" + self.ns["lido"] + "measurementType")
            mm_nodes = mnd.findall(self.ns["lido"] + "measurementsSet/" + self.ns["lido"] + "measurementValue")
            try:            
                height = mm_nodes[0].text if dim_nodes[0].text == "Höhe" else mm_nodes[1].text
                width = mm_nodes[1].text if dim_nodes[1].text == "Breite" else mm_nodes[0].text
            except:
                continue
            if type == "Blatt":
                self.dim_sheet = (height, width)
            if type == "Platte":
                self.dim_plate = (height, width)
    def get_subjects(self):
        subject_nodes = self.node.findall(".//" + self.ns["lido"] + "subject")
        for snd in subject_nodes:
            terms = [nd.text for nd in snd.findall(self.ns["lido"] + "subjectConcept/" + self.ns["lido"] + "term") if nd.text is not None]
            if None in terms:
                print(terms)
                return
            try:
                ic_not = snd.find(f"{self.ns['lido']}subjectConcept/{self.ns['lido']}conceptID").text
            except:
                self.subjects = list(terms)
            else:
                self.iconclass_notation = ic_not
                self.iconclass_labels = list(terms)
    def getLinks(self):
        repp = self.node.findall(".//" + self.ns["lido"] + "resourceRepresentation")
        for rp in repp:
            rty = rp.get(self.ns["lido"] + "type")
            try:
                link = rp.findall(".//" + self.ns["lido"] + "linkResource")[0].text
            except:
                continue
            if rty == "display":
                self.image = link
            elif rty == "thumbnail":
                self.thumb = link
            elif rty == "purl":
                self.purl = link                    
    def getFieldValues(self, field):
        ret = []
        ndd = self.node.findall(".//" + self.ns["lido"] + field)
        for nd in ndd:
            ret.append(nd.text)
        return(ret)
    def getPathValues(self, path):
        ret = []
        ndd = self.node.findall(path)
        for nd in ndd:
            ret.append(nd.text)
        return(ret)
class Person():
    def __init__(self, persName):
        self.persName = persName
        self.role = ""
    def __str__(self):
        ret = self.persName
        if self.role != "":
            ret = ret.strip() + " (" + self.role + ")"
        return(ret)