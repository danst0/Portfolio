#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uuid

class Money:
	def __init__(self, data, portfolio):
		self.data = data
		self.portfolio = portfolio
	def row_exists(self, typus, date):
#		print(typus, date)
		result = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date = ?''', (typus, date)).fetchone()
		return False if result == None else True
	def update(self, typus, date, value):
		if typus != 'settlement' and self.row_exists(typus, date):
			self.data.c.execute('''UPDATE money SET value = ? WHERE type = ? AND date = ?''', (value, typus, date))
		else:
			self.data.c.execute('''INSERT INTO money(id, type, date, value) VALUES (?, ?, ?, ?)''', (uuid.uuid4(), typus, date, value))
		self.data.commit()	
	def add_income(self, date, income):
		self.update('income', date, income)
			
	def add_total(self, date, total):
		self.update('total', date, total)
	
	def get_all(self, from_date, to_date):
		old_total = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date <= ? ORDER BY date DESC''', ('total', from_date)).fetchone()
#		print(old_total)
		new_total = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date <= ? ORDER BY date DESC''', ('total', to_date)).fetchone()
#		print(new_total)
		tmp_income = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date > ? AND date <= ? ORDER BY date DESC''', ('income', from_date, to_date)).fetchall()
		tmp_settlement = self.data.c.execute('''SELECT value FROM money WHERE type = ? AND date > ? AND date <= ? ORDER BY date DESC''', ('settlement', from_date, to_date)).fetchall()
#		print(tmp_settlement)
#		print(tmp_income)
		if old_total != None:
			old_total = old_total[0]
		else:
		    old_total = 0.0
		if new_total != None:
			new_total = new_total[0]
		income = 0.0
		if tmp_income != None:
			for i in tmp_income:
				income += i[0]
		if tmp_settlement != None:
			for i in tmp_settlement:
				income += i[0]
#		print(income)
		portfolio_value_at_start, invest, divest, portfolio_value_at_end, dividend, profit_on_books_wo_dividend = self.portfolio.profitability(from_date, to_date)
		print('Old cash value ' + str(old_total))
		print('Old PF value ' + str(portfolio_value_at_start))
		print('Income ' + str(income))
		print('Invest/Divest ' + str(invest) + '/' + str(divest))
		print('Dividend ' + str(dividend))
		income_from_stocks = -invest + divest + dividend
		print('Income from stocks ', income_from_stocks)
		# Negative is expense, positive is 
		expense = new_total - old_total + income_from_stocks
		print('Expense ', expense)

		print('Profit on books', portfolio_value_at_end - portfolio_value_at_start)

		print('New cash value ' + str(new_total))
		print('New PF value ' + str(portfolio_value_at_end))

		print('Informational (incl. in pf): Profit on books ' + str(profit_on_books_wo_dividend))
		