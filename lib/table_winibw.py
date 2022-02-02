#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
from lib import localsql as ls
from lib import shelfmark as sm
from lib import csvt

# Verarbeitung von CSV-Tabellen, die in der WinIBW generiert und unter path abgelegt wurden
class Table():
    def __init__(self, path):
        try:
            file = open(path, "r", encoding="cp1252")
        except:
            print("Keine Datei unter " + path)
            return(None)
        reader = csv.DictReader(file, delimiter=";")
        self.content = [row for row in reader]
        fieldDict = self.content.pop(0)
        self.fields = [tup for tup in fieldDict if tup != ""]
    def __iter__(self):
        self.a = 0
        return(self)
    def __next__(self):
        if self.a < len(self.content):
            ret = self.content[self.a]
            self.a += 1
            return(ret)
        else:
            raise StopIteration            
    def getByField(self, field):
        ret = [row[field] for row in self.content]
        return(ret)
    def getSelection(self, fields):
        ret = [[row[field] for field in fields] for row in self.content]
        return(ret)
    def filter(self, function = lambda row : row):
        self.content = [function(row) for row in self.content]
        # Gibt die function None aus, wird die entsprechende Zeile entfernt
        self.content = [row for row in self.content if row != None]
        return(self.content)
    def addSortable(self, field = "Signatur"):
        if field not in self.fields:
            print("Keine Spalte " + field + " gefunden.")
            return(False)
        self.fields.append("Sortierform")
        for row in self.content:
            sig = sm.StructuredShelfmark(row[field])
            row["Sortierform"] = sig.sortable
        return(True)
    def addParallels(self, fieldMan = "PPN", fieldEx = "Signatur"):
        if fieldMan not in self.fields:
            print("Keine Spalte " + fieldMan + " gefunden.")
            return(False)
        if fieldEx not in self.fields:
            print("Keine Spalte " + fieldEx + " gefunden.")
            return(False)
        for row in self.content:
            parallels = []
            for rowSub in self.content:
                if row[fieldMan] == rowSub[fieldMan] and row[fieldEx] != rowSub[fieldEx]:
                    parallels.append(rowSub[fieldEx])
            row["Parallelexemplare"] = ";".join(parallels)
        self.fields.append("Parallelexemplare")
    def save(self, fileName = "myTable"):
        body = [[row[key] for key in row] for row in self.content]
        table = csvt.Table(self.fields, body)
        table.save(fileName)
    def toSQLite(self, fileName = "exportTable"):
        db = ls.Database(self.fields, [[row[field] for field in self.fields] for row in self.content], fileName)
        return(True)        