#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tracking on Income and expense
# Monthly tracking 1 time entry per 31st
# Regular and one time component
# Overall delta in wealth
#


class Portfolio:
	"""Collection of different portfolios or stocks."""
	def __init__(self, name, transaction):
		self.name = name	

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
		stocks_at_start = self.transaction.get_portfolio('All', from_date.strftime("%Y-%m-%d"))
		print(stocks_at_start)
		portfolio_value_at_start = 0.0
		for key in stocks_at_start.keys():
			portfolio_value_at_start += stocks_at_start[key] * self.prices.get_price(key, from_date.strftime("%Y-%m-%d"))
		stocks_at_end = self.transaction.get_portfolio('All', to_date.strftime("%Y-%m-%d"))
		portfolio_value_at_end = 0.0
		for key in stocks_at_end.keys():
			portfolio_value_at_end += stocks_at_end[key] * self.prices.get_price(key, to_date.strftime("%Y-%m-%d"))

		invest = self.transaction.get_total_invest('All', from_date, to_date)
		divest = self.transaction.get_total_divest('All', from_date, to_date)
		dividend = self.transaction.get_total_dividend('All', from_date, to_date)

		profit_incl_on_books = portfolio_value_at_end + invest - divest - portfolio_value_at_start + dividend
		print('Absolute KPIs')
		keys = ['Start portfolio', 'Investment', 'Divestment', 'Current portfolio', 'Dividend', 'Profit (incl. on books)']
		x = PrettyTable(keys)
		x.padding_width = 1 # One space between column edges and contents (default)
		x.add_row([portfolio_value_at_start, -invest, divest, portfolio_value_at_end, dividend, profit_incl_on_books])
		print(str(x))
		print('Relative KPIs')		  
		keys = ['ROI']
		x = PrettyTable(keys)
		x.padding_width = 1 # One space between column edges and contents (default)
		x.add_row([str(round(profit_incl_on_books/(portfolio_value_at_start - invest)*100,2)) + '%'])
		print(str(x))