#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import logging

class Table:
    encoding = "utf-8"
    def __init__(self, fields = None, content = None):
        self.content = []
        self.fields = []
        if content != None:
            self.content = content
        if fields != None:
            self.fields = fields
    def save(self, path, delimiter = ";"):
        with open(path + ".csv", 'w', encoding=self.encoding, newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=delimiter, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.fields)
            for row in self.content:
                writer.writerow(row)
        return(True)
    def load(self, path):
        try:
            file = open(path + ".csv", "r", encoding = self.encoding)
        except:
            print("Keine Datei unter " + path)
            return(False)
        reader = csv.reader(file, delimiter=";")
        self.content = [row for row in reader]
        if self.fields == []:
            self.fields = self.content.pop(0)
        return(True)
class TableWin(Table):
    encoding = "cp1252"
class TableGeoBrowser(Table):
    def __init__(self, content = None):
        super().__init__(content)
        self.fields = ["Name", "Address", "Description", "Longitude", "Latitude", "TimeStamp", "TimeSpan:begin", "TimeSpan:end", "GettyID", "Weight"]
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
        return(True)            
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
        self.getty = ""
        self.weight = 1
        if weight != None:
            self.weight = weight
    def to_list(self):
        return([self.name, self.address, self.description, self.long, self.lat, self.timeStamp, "", "", self.getty, self.weight])