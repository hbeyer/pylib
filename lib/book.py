#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Edition:
    def __init__(self):
        self.ppn = None
        self.bibliography = None
        self.id = None
        self.bbg = None
        self.authors = []
        self.persons = []
        self.title = None
        self.date = None
        self.places = []
        self.printers = []
        self.pages = None
        self.subjects = []
        self.digi = None
        self.shelfmarks = []
        self.copies = []
    def __str__(self):
        ret = self.__class__.__name__ + ": " + self.title[0:20] + ", " + self.bibliography + " " + self.id + ", ";
        if self.places:
            ret = ret + "/".join(self.places) +  " "
        ret = ret + self.date
        return(ret)
    def flatten(self):
        ret = [self.ppn, self.bibliography, self.id, self.bbg, self.title, "/".join(self.authors), "/".join(self.places), "/".join(self.printers), self.date, self.pages, "|".join(self.subjects), "|".join(self.shelfmarks), self.digi]
        return(ret)
    def fieldList(self):
        return("PPN", "Bibliographie", "ID", "BBG", "Titel", "Verfasser", "Orte", "Drucker", "Jahr", "Umfang", "Gattungsbegriffe", "Signaturen", "Digitalisierung")
Edition.fieldList = classmethod(Edition.fieldList)
class EditionVD17(Edition):
    def __init__(self):
        super().__init__()
        self.bibliography = "VD17"