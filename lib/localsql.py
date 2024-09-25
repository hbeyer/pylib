#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import logging

class Database():
    def __init__(self, file_name = None):
        self.file_name = "mydb"
        if file_name != None:
            self.file_name = file_name
    def insert_content(self, fields, content):
        self.erase()
        self.conn = sqlite3.connect(self.file_name + ".db")
        self.cursor = self.conn.cursor()
        self.fields = [field.replace("+", "") for field in fields]
        sql = "CREATE TABLE main (" + (", ".join(fields)) + ")"
        self.cursor.execute(sql)
        for row in content:
            sql = "INSERT INTO main VALUES (" + ", ".join(["?" for field in self.fields]) + ")"
            self.cursor.execute(sql, row)
        self.conn.commit()
        self.conn.close()
        logging.info("Es wurde die Datenbank \"" + self.file_name + ".db\" mit der Tabelle \"main\" und den Feldern \"" + ", ".join([field for field in self.fields]) + "\" angelegt.")
        return(True)
    def erase(self):
        try:
            os.remove(self.file_name + ".db")
        except:
            return(False)
        return(True)
    def sql_action(self, command):
        self.conn = sqlite3.connect(self.file_name + ".db")
        self.curs = self.conn.cursor()
        self.curs.execute(command)
        self.conn.commit()
        self.conn.close()
        return(True)
    def sql_mult_action(self, commands):
        self.conn = sqlite3.connect(self.file_name + ".db")
        self.curs = self.conn.cursor()
        for com in commands:
            self.curs.execute(com)
            self.conn.commit()
        self.conn.close()
        return(True)
    def sql_request(self, sql):
        if "select" not in sql.lower():
            logging.error("Das SQL-Kommando muss SELECT enthalten")
            return(None)
        self.conn = sqlite3.connect(self.file_name + ".db")
        self.curs = self.conn.cursor()
        self.curs.execute(sql)
        res = self.curs.fetchall() 
        self.conn.close()
        return(res)
    def sql_mult_request(self, commands):
        for sql in commands:
            if "select" not in sql.lower():
                logging.error("Die SQL-Kommandos müssen SELECT enthalten")
                return(None)
        res = []
        self.conn = sqlite3.connect(self.file_name + ".db")
        self.curs = self.conn.cursor()
        for com in commands:
            self.curs.execute(com)
            res.append(self.curs.fetchall())
        self.conn.close()
        return(res)        
    def get_description(self):
        ret = {}
        sql = "PRAGMA table_list"
        table_list = self.sql_request(sql)
        for schema, name, type, ncol, wr, strict in table_list:
            sql_ti = f"PRAGMA {schema}.table_info({name})"
            table_info = self.sql_request(sql_ti)
            ret[name] = { "schema" : schema, "type" : type, "ncol" : ncol, "columns" : [{ "id" : info[0], "colname" : info[1], "type": info[2], "notnull" : info[3], "default" : info[4], "primkey" : info[5] } for info in table_info] }
        return(ret)
    def print_description(self, verbose = True):
        descr = self.get_description()
        for key, data in descr.items():
            if key in ["sqlite_schema", "sqlite_temp_schema"] and verbose == False:
                continue
            print(f"Tabelle \"{key}\", ({data['ncol']} Spalten):\n")
            for coldict in data["columns"]:
                coltype = coldict["type"]
                if coltype == "":
                    coltype = "no data type"
                print(f"\tSpalte \"{coldict['colname']}\" ({coltype})\n")
        return(True)
    def fetch_dict(self):
        with sqlite3.connect(self.file_name + ".db") as conn:
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

# Abgeleitete Klasse, für den Fall, dass man die Datenbankverbindung 
# für komplexere Berechnungen offen halten will
class DataConnection(Database):
    def __init__(self, file_name):
        super().__init__(file_name)
        self.conn = sqlite3.connect(self.file_name + ".db")
        self.curs = self.conn.cursor()
    def close(self):
        self.conn.close()
        return(True)
    def sql_request(self, sql):
        self.curs.execute(sql)
        res = self.curs.fetchall()
        return(res)