#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid

class Money:
	def __init__(self, data, portfolio):
		self.data = data
		self.portfolio = portfolio
	def row_exists(self, typus, date):
# 		print(typus, date)
		result = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date = ?''', (typus, date)).fetchone()
		return False if result == None else True
	def update(self, typus, date, value):
		if self.row_exists(typus, date):
			self.data.c.execute('''UPDATE money SET value = ? WHERE type = ? AND date = ?''', (value, typus, date))
		else:
			self.data.c.execute('''INSERT INTO money(id, type, date, value) VALUES (?, ?, ?, ?)''', (uuid.uuid4(), typus, date, value))	  
	def add_income(self, date, income):
		self.update('income', date, income)
			
	def add_total(self, date, total):
		self.update('total', date, total)
	
	def get_all(self, from_date, to_date):
	    old_total = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date <= ? ORDER BY date ASC''', ('total', from_date)).fetchone()
	    print(old_total)
	    new_total = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date <= ? ORDER BY date ASC''', ('total', to_date)).fetchone()
	    print(new_total)
		income, expense, portfolio, total = 0,0,0,0
		return income, expense, portfolio, total
