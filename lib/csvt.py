#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv

class Table:
    def __init__(self, fields = [], content = []):
        self.content = content
        self.fields = fields
    def save(self, path, encoding = "utf-8"):
        with open(path + ".csv", 'w', encoding=encoding, newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.fields)
            for row in self.content:
                writer.writerow(row)
        return(True)
    def load(self, path, encoding = "utf-8"):
        try:
            file = open(path + ".csv", "r", encoding = encoding)
        except:
            print("Keine Datei unter " + path)
            return(False)
        reader = csv.reader(file, delimiter=";")
        self.content = [row for row in reader]
        if self.fields == []:
            self.fields = self.content.pop(0)
        return(True)
