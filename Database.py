#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import uuid

class Database:
	def __init__(self):
		sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes=b))
		sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes)

		self.conn = sqlite3.connect('data.sql', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
		self.c = self.conn.cursor()
		# Create tables	   
		try:
			self.c.execute('''CREATE TABLE transactions (id GUID PRIMARY KEY, type TEXT, portfolio TEXT, stock_id GUID, date TEXT, nominal REAL, price REAL, cost REAL, total REAL)''')
		except:
			pass
		else:
			print('Created table for transactions')
		try:
			self.c.execute('''CREATE TABLE stocks (id GUID PRIMARY KEY, name TEXT, aliases TEXT, yahoo_id TEXT, type TEXT)''')
		except:
			pass
		else:
			print('Created table for stocks')
		try:
			self.c.execute('''CREATE TABLE prices (id GUID PRIMARY KEY, stock_id GUID, date TEXT, price REAL)''')
		except:
			pass
		else:
			print('Created table for prices')
		try:
			self.c.execute('''CREATE TABLE money (id GUID PRIMARY KEY, date TEXT, type TEXT, value REAL)''')
		except:
			pass
		else:
			print('Created table for money')

	def commit(self):
		self.conn.commit()
	def close(self):
		self.conn.commit()
		self.conn.close()