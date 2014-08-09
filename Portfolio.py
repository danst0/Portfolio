#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Tracking on Income and expense
# Monthly tracking 1 time entry per 31st
# Regular and one time component
# Overall delta in wealth
#


class Portfolio:
	"""Collection of different portfolios or stocks."""
	def __init__(self, name, parent=None):
		self.parent = parent
		self.name = name
		self.children = []
		self.child_securities = []
		self.cash = 0.0
	def adjust_cash(self, value):
		self.cash += value
	def get_cash(self):
		return self.cash
	def add_security(self, parent, stock_id):
		if self.name == parent:
			self.child_securities.append(stock_id)
		else:
			for i in self.children:
				i.add_security(parent, stock_id)
	def add_portfolio(self, parent, name):
		if self.name == parent:
			self.children.append(Portfolio(name, parent))
		else:
			for i in self.children:
				i.add_portfolio(parent, name)
	def __repr__(self, level=1):
		output = self.name + '\n'
		for i in self.children:
			output += 'Available cash: ' + i.get_cash() + '\n'
			output += '	   '*level + '+-- ' + i.__str__(level+1)
		return output