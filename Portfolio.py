#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tracking on Income and expense
# Monthly tracking 1 time entry per 31st
# Regular and one time component
# Overall delta in wealth
#
from prettytable import PrettyTable

class Portfolio:
	"""Collection of different portfolios or stocks."""
	def __init__(self, name, transaction, prices):
		self.name = name
		self.transaction = transaction
		self.prices = prices

	def add_portfolio(self, parent, name):
		if self.name == parent:
			self.children.append(Portfolio(name, parent))
		else:
			for i in self.children:
				i.add_portfolio(parent, name)
	def __repr__(self, level=1):
		output = self.name + '\n'
		return output

	def profitability(self, from_date, to_date):
		stocks_at_start = self.transaction.get_portfolio('All', from_date)
# 		print(stocks_at_start)
		portfolio_value_at_start = 0.0
		for key in stocks_at_start.keys():
			price = self.prices.get_price(key, from_date)
			if price == None:
				price = 0.0
			portfolio_value_at_start += stocks_at_start[key] * price
		stocks_at_end = self.transaction.get_portfolio('All', to_date)
		portfolio_value_at_end = 0.0
		for key in stocks_at_end.keys():
			price = self.prices.get_price(key, to_date)
			if price == None:
				price = 0.0
			portfolio_value_at_end += stocks_at_end[key] * price

		invest = self.transaction.get_total_invest('All', from_date, to_date)
		divest = self.transaction.get_total_divest('All', from_date, to_date)
		dividend = self.transaction.get_total_dividend('All', from_date, to_date)

		profit_on_books_wo_dividend = portfolio_value_at_end + invest - divest - portfolio_value_at_start
		return portfolio_value_at_start, -invest, divest, portfolio_value_at_end, dividend, profit_on_books_wo_dividend
	def list_pf(self, at_date)
		stocks = self.transaction.get_portfolio('All', at_date.strftime("%Y-%m-%d"))
#		  print(stocks)
		keys = ['Name', 'Nominal', 'Price', 'Value']		
		x = PrettyTable(keys)
		x.padding_width = 1 # One space between column edges and contents (default)
		x.align["Price"] = "r"
		x.align["Value"] = "r"
		x.align["Nominal"] = "r"
		prices = []
		tmp = 0.0
		for key in stocks.keys():
			price = self.prices.get_price(key, my_date.strftime("%Y-%m-%d"))
			value = 0.0
			if price != None:
				value = stocks[key] * price
			else:
				print('Price for ' + self.secs.get_name_from_stock_id(key) + ' missing; assuming zero')
			x.add_row([self.secs.get_name_from_stock_id(key),
						self.nice_number(stocks[key]),
						self.nice_number(price),
						self.nice_number(value)])
			tmp += value
		x.add_row(4*['====='])
		x.add_row(['Total', '----', '----', tmp])
		print(str(x))
