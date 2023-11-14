#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import logging
import re
import copy
from lib import localsql as ls
from lib import shelfmark as sm

class Table:
    encoding = "utf-8"
    def __init__(self, fields = None, content = None):
        self.content = []
        self.fields = []
        if content != None:
            self.content = content
        if fields != None:
            self.fields = fields
    def __iter__(self):
        self.a = 0
        return(self)
    def __next__(self):
        if self.a < len(self.content):
            ret = self.get_row_dict(self.content[self.a])
            self.a += 1
            return(ret)
        else:
            raise StopIteration     
    def get_row_dict(self, row):
        newrow = copy.copy(row)
        ret = {}
        for field in self.fields:
            ret[field] = newrow.pop(0)
        return(ret)
    def to_dict(self):
        return([self.get_row_dict(row) for row in self.content])
    def save(self, path, delimiter = ";"):
        with open(path + ".csv", 'w', encoding=self.encoding, newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.fields)
            for row in self.content:
                writer.writerow(row)
        return(True)
    def add_row(self, name):
        self.fields.append(name)
        for row in self.content:
            row.append("")
    def add_sortable(self, field = None):
        if field == None:
            field = "Signatur"
        if field not in self.fields:
            print("Keine Spalte " + field + " gefunden.")
            return(False)
        for row in self.content:
            row_dict = self.get_row_dict(row)
            sm_orig = row_dict[field]
            sig = sm.StructuredShelfmark(sm_orig)
            row.append(sig.sortable)
        self.fields.append("Sortierform")
        return(True)        
    def load(self, path):
        try:
            file = open(path + ".csv", "r", encoding = self.encoding)
        except:
            print("Keine Datei unter " + path)
            return(False)
        reader = csv.reader(file, delimiter=";")
        self.content = [list(map(str.strip, row)) for row in reader]
        if self.fields == []:
            fields = self.content.pop(0)
            fields = map(str.strip, fields)
            fields = list(fields)
            self.fields = fields
        return(True)
    def get_index(self, field):
        index = {}
        for row in self:
            if row[field] in ["", "NULL"]:
                continue
            try:
                index[row[field]].append(row)
            except:
                index[row[field]] = [row]
        return(index)
    def toSQLite(self, fileName = "exportTable"):
        db = ls.Database(fileName)
        db.insert_content(self.fields, self.content)
        return(True)
class TableWin(Table):
    encoding = "cp1252"
class TableGeoBrowser(Table):
    def __init__(self, content = None):
        super().__init__(content)
        self.fields = ["Name", "Address", "Description", "Longitude", "Latitude", "TimeStamp", "TimeSpan:begin", "TimeSpan:end", "GettyID", "weight"]
        if content != None:
            for row in content:
                self.import_row(row)
    def import_row(self, row):
        if type(row) != GeoDataRow:
            logging.error(f"Ungültiger Geodatensatz übergeben: {str(row)}")
            return(False)
        self.content.append(row.to_list())
    def simplify_content(self):
        index = {}
        for row in self.content:
            try:
                index[row[0] + row[1] + row[5]][9] += row[9]
            except:
                index[row[0] + row[1] + row[5]] = row
        self.content = []
        for ind, data in index.items():
            self.content.append(data)
    def fill_geo_data(self, gdb):
        for row in self.content:
            if row[3] == "" or row[4] == "":
                row[3], row[4] = gdb.get_coord(row[0])
        self.remove_void()
        return(True)
    def remove_void(self):
        new_content = [row for row in self.content if row[3] != ""]
        self.content = new_content
    def save(self, path):
        with open(path + ".csv", 'w', encoding=self.encoding, newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.fields)
            for row in self.content:
                writer.writerow(row)
        return(True)
class GeoDataRow:
    def __init__(self, name=None, long=None, lat=None, timeStamp=None, weight=None):
        self.name = ""
        if name != None:
            self.name = name
        self.address = ""       
        self.description = ""
        self.long = ""
        if long != None:
            self.long = long
        self.lat = ""
        if lat != None:
            self.lat = lat        
        self.timeStamp = ""
        if timeStamp != None:
            self.timeStamp = timeStamp
            if re.match(r"1\d\d\d$", self.timeStamp):
                self.timeStamp = self.timeStamp + "-01-01"
        self.getty = ""
        self.weight = 1
        if weight != None:
            self.weight = weight
    def to_list(self):
        return([self.name, self.address, self.description, self.long, self.lat, self.timeStamp, "", "", self.getty, str(self.weight)])