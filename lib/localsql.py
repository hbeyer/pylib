#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import logging

class Database():
    def __init__(self, fields = None, content = None, fileName = None):
        self.fields = fields
        self.fileName = "mydb"
        if fileName != None:
            self.fileName = fileName
        try:
            os.remove(self.fileName + ".db")
        except:
            pass        
        self.conn = sqlite3.connect(self.fileName + ".db")
        self.cursor = self.conn.cursor()
        fields = [field.replace("+", "") for field in self.fields]
        sql = "CREATE TABLE main (" + (", ".join(fields)) + ")"
        self.cursor.execute(sql)
        for row in content:
            sql = "INSERT INTO main VALUES (" + ", ".join(["?" for field in self.fields]) + ")"
            self.cursor.execute(sql, row)
        self.conn.commit()
        self.conn.close()
        logging.info("Es wurde die Datenbank \"" + fileName + ".db\" mit der Tabelle \"main\" und den Feldern \"" + ", ".join([field for field in fields]) + "\" angelegt.")
    def fetch_dict(self):
        with sqlite3.connect(self.fileName + ".db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM main")
            result = cursor.fetchall()
            ret = []
            for row in result:
                insert = {}
                for field in self.fields:
                    insert[field] = row.pop(0)
                ret.append(insert)
            return(ret)