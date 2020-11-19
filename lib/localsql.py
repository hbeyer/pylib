#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import os

class Database():
	def __init__(self, fields, content, fileName = "mydb"):
		self.fields = fields
		try:
			os.remove(fileName + ".db")
		except:
			pass
		conn = sqlite3.connect(fileName + ".db")
		cursor = conn.cursor()
		fields = [field.replace("+", "") for field in self.fields]
		sql = "CREATE TABLE main (" + (", ".join(fields)) + ")"
		cursor.execute(sql)
		for row in content:
			sql = "INSERT INTO main VALUES (" + ", ".join(["?" for field in self.fields]) + ")"
			cursor.execute(sql, row)
		conn.commit()
		conn.close()
		print("Es wurde die Datenbank \"" + fileName + ".db\" mit der Tabelle \"main\" und den Feldern \"" + ", ".join([field for field in fields]) + "\" angelegt.")