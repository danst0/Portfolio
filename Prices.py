#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime		
import ystockquote
import urllib
import re
import uuid
from input_methods import *

class Prices:
	"""Class to store price developments."""
	numbers = {}
	def __init__(self, data):
		self.data = data
		self.secs = None
		self.numbers = {}
		all = self.data.c.execute('SELECT * FROM prices')
#		print('Preise initialisieren')
		for line in all.fetchall():
			id = line[1]
			date = line[2]
			price = line[3]
			if id not in self.numbers.keys():
				self.numbers[id] = {}
			self.numbers[id][date] = price
	def delete_prices(self, isin_id):
		stock_id = self.secs.get_stock_id_from_isin_id(isin_id)
		self.data.c.execute('''DELETE FROM prices WHERE stock_id = ?''', (stock_id, ))
	def get_dates_and_prices(self, isin_id, from_date, to_date=datetime.date.today().strftime('%Y-%m-%d')):
		stock_id = self.secs.get_stock_id_from_isin_id(isin_id)
		if from_date == None:
			from_date = '1900-01-01'
		result = self.data.c.execute('''SELECT date, price FROM prices WHERE stock_id = ? AND date >= ? AND date <= ? ORDER BY date''', (stock_id, from_date, to_date)).fetchall()
		# Redo with map function
		dates = []
		values = []
		for item in result:
			dates.append(datetime.datetime.strptime(item[0], "%Y-%m-%d").date())
			values.append(item[1])			  
		return dates, values
	def find_split_date(self, isin_id):
		stock_id = self.secs.get_stock_id_from_isin_id(isin_id)
		prices = self.get_prices(stock_id)
		old_price = None
		last_unsplit_date = None
		suggested_ratio = None
		for date in reversed(sorted(prices)):
			new_price = prices[date]
			if old_price != None:
				if new_price/float(old_price) > 1.5:
					last_unsplit_date = date
					suggested_ratio = int(round(new_price/float(old_price), 0))
					break
			old_price = new_price
		return last_unsplit_date, suggested_ratio		  

	def row_exists(self, stock_id, date):
		result = self.data.c.execute('''SELECT price FROM prices WHERE stock_id = ? AND date = ?''', (stock_id, date)).fetchone()
		return False if result == None else True
	def update(self, isin_id, date, price, interactive=False, alt_name=''):
#		print('date for price update ', date)
		if not isin_id and interactive:
				print(self.secs)
				print('No valid ISIN given for', alt_name)
				tmp = input_string('Which stock is it?')
				tmp_stock = self.secs.find_stock(tmp, return_obj=True)
				isin_id = tmp_stock.isin_id
				tmp_stock.aliases.append(alt_name)
				self.secs.change_stock(isin_id, tmp_stock)
		elif not isin_id:
			print('No valid ISIN given.')
        if isin_id:
            id = self.secs.get_stock_id_from_isin_id(isin_id)
            if id not in self.numbers.keys():
                self.numbers[id] = {}
            self.numbers[id][date] = price
            if self.row_exists(id, date):
                self.data.c.execute('''UPDATE prices SET price = ? WHERE stock_id = ? AND date = ?''', (price, id, date))
            else:
                self.data.c.execute('''INSERT INTO prices(id, stock_id, date, price) VALUES (?, ?, ?, ?)''', (uuid.uuid4(), id, date, price))
	def get_price(self, stock_id, date, none_equals_zero=False):
		"""Return price at given date or up to four days earlier"""
		price = None
		if none_equals_zero:
			price = 0.0
		for i in range(4):
			date = (datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
			try:
				price = self.numbers[stock_id][date]
			except:
				pass
		return price
	def get_prices(self, stock_id, before_date=None):
		prices = None
		if stock_id in self.numbers.keys():
			prices = self.numbers[stock_id]
#		print(prices)
		if prices and before_date:
			prices = { k: v for k, v in prices.items() if k <= before_date }
		return prices
	def get_last_price(self, isin_id, before_date=None, none_equals_zero=False):
		stock_id = self.secs.get_stock_id_from_isin_id(isin_id)
		return self.get_last_price_from_stock_id(stock_id, before_date, none_equals_zero)	
	def get_last_price_from_stock_id(self, stock_id, before_date=None, none_equals_zero=False):
		"""Return last price available, if given, return last price available before given date"""
		prices = self.get_prices(stock_id, before_date)
		if prices:
			max_key = max(prices.keys())
			return prices[max_key]
		else:
			if none_equals_zero:
				return 0.0
			else:
				return None
	def get_quote(self, symbol):
		print(symbol)
		base_url = 'http://www.boerse-frankfurt.de/en/search/result?order_by=wm_vbfw.name&name_isin_wkn='
		content = urllib.request.urlopen(base_url + symbol).read().decode('UTF-8')#.replace('\n','')

		quote = None
		m = re.search('Last Price.{1,100}<span.{1,45}security-price.{1,55}>([0-9\.]{3,9})<\/', content, re.DOTALL)
		if m:
			quote = float(m.group(1))
		else:
			print('Error: could not retrieve quote')
		return quote
	def __str__(self):
		keys = ['ID', 'Date', 'Price']
		x = PrettyTable(keys)
		x.align[keys[0]] = "l" # Left align city names
		x.padding_width = 1 # One space between column edges and contents (default)
		for key in self.numbers.keys():
			for dates in self.numbers[key].keys():
				x.add_row((key, dates, self.numbers[key][dates]))
		return str(x)
