#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime		
import ystockquote
import urllib
import re
import uuid

class Prices:
	"""Class to store price developments."""
	numbers = {}
	def __init__(self, data):
		self.data = data
		self.secs = None
		self.numbers = {}
		all = self.data.c.execute('SELECT * FROM prices')
		print('Preise initialisieren')
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
		stock_id = self.get_stock_id_from_isin_id(isin_id)
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
		prices = self.get_prices(isin_id)
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
	def update(self, isin_id, date, price):
#		print('date for price update ', date)
		id = self.secs.get_stock_id_from_isin_id(isin_id)
		if id not in self.numbers.keys():
			self.numbers[id] = {}
		self.numbers[id][date] = price
		if self.row_exists(id, date):
			self.data.c.execute('''UPDATE prices SET price = ? WHERE stock_id = ? AND date = ?''', (price, id, date))
		else:
			self.data.c.execute('''INSERT INTO prices(id, stock_id, date, price) VALUES (?, ?, ?, ?)''', (uuid.uuid4(), id, date, price))
	def get_price(self, id, date):
		price = None
		for i in range(4):
			date = (datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
			try:
				price = self.numbers[id][date]
			except:
				pass
		return price
	def get_prices(self, isin_id):
		id = self.secs.get_stock_id_from_isin_id(isin_id)
		prices = None
		try:
			prices = self.numbers[isin_id]
		except:
			pass
		return prices
	def get_last_price(self, isin_id, none_equals_zero=False):
		id = self.secs.get_stock_id_from_isin_id(isin_id)
#		print(isin_id, id)
#		  pdb.set_trace()
		prices = self.get_prices(id)
#		  print(prices)
		if prices != None:
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
