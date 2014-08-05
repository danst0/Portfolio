#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from prettytable import PrettyTable

class UI:
	"""Class to display user interface."""
	def __init__(self, securities, portfolio, prices, transaction):
		self.secs = securities
		self.portfolio = portfolio
		self.prices = prices
		self.transaction = transaction
		self.last_update = datetime.datetime.now() + datetime.timedelta(days=-1)
		go_on = True
		while go_on:
			go_on = self.main_menu()

	def get_historic_quotes(self):
		print('Start update')
			
		now = datetime.datetime.now()
#		  print(now, self.last_update)
		if now < self.last_update + datetime.timedelta(seconds=90):
			print('Please leave at least 30 secs between each update.')
			return
		else:
			self.last_update = now
		today = datetime.date.today()
		first_day = datetime.date.today() - datetime.timedelta(days=15*365)
		today_str = today.strftime('%Y-%m-%d')
		first_day_str = first_day.strftime('%Y-%m-%d')
		for sec in self.secs:
			quote = None
			try:
				quote = ystockquote.get_historical_prices(sec.yahoo_id, first_day_str, today_str)
			except urllib.error.HTTPError:
				print('No quotes found for:', sec.name)
				self.last_update += datetime.timedelta(seconds=-90)
			else:
#				  print(quote)
				for key in quote:
					self.prices.update(sec.yahoo_id, key, quote[key]['Close'])
		print('Update finished')
					
	def update_stocks(self):
		print('Start update')
		now = datetime.datetime.now()
		if now < self.last_update + datetime.timedelta(seconds=30):
			print('Please leave at least 30 secs between each update.')
			return
		else:
			self.last_update = now
		today = datetime.date.today()
		if today.weekday() >= 5:
			today = today + datetime.timedelta(days=4-today.weekday())
		yesterday = today + datetime.timedelta(days=-1)
		day_str = today.strftime('%Y-%m-%d')
		yesterday_str = yesterday.strftime('%Y-%m-%d')
		for sec in self.secs:
			quote = None
			quote = self.prices.get_quote(sec.yahoo_id)
			if not quote:
				print('No quotes found for:', sec.name)
				self.last_update += datetime.timedelta(seconds=-30)
			else:
				self.prices.update(sec.yahoo_id, day_str, quote)
		print('Update finished')		
				
	def list_stocks(self):
		if not self.secs.empty():
			print(self.secs)
		else:
			print('No stocks in database.')
	def new_stock(self):
		print('Name ',) 
		name = input()
		print('Aliases (comma separated) ',) 
		aliases = input().split(',')
#		  print(aliases)
		for num in range(len(aliases)):
			aliases[num] = aliases[num].strip()
		print ('ID ',)
		id = input()
		print ('Type ',)
		type = input()
		self.secs.add(name, aliases, id, type)
	def list_content(self):

		pf = input('Portfolio [All] ')
		if pf == '':
			pf = 'All'
		transactions = self.transaction.get_total_for_portfolio(pf)
#		  print(transactions)
		
		x = PrettyTable(['ID', 'Nominal', 'Cost', 'Value'])
		x.align['Invested'] = "l" # Left align city names
		x.padding_width = 1 # One space between column edges and contents (default)
#		  print(transactions)
		for i in transactions:
#			  print(i)
			x.add_row(i[:-1] + (self.prices.get_last_price(i[0],) * i[1],))
		print(x)

	def new_portfolio(self):
		print(self.portfolio)
		print('Parent ',) 
		parent = input()
		
		print('Name ',) 
		name = input()

		self.portfolio.add(parent, name)
	def new_graph(self):
		print('Security',)
		stock = input()
		tmp_default = (datetime.date.today() - datetime.timedelta(days=12*30)).strftime('%Y-%m-%d')
		print('Start date [' + tmp_default + ']',)
		from_date = input()
		if from_date == '':
			from_date = tmp_default
		from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
		tmp_default = datetime.date.today().strftime('%Y-%m-%d')
		print('End date [' + tmp_default + ']',)
		to_date = input()
		if to_date == '':
			to_date = tmp_default
		to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
		dates, values = self.prices.get_dates_and_prices(self.secs.find_stock(stock), from_date, to_date)
		plt.plot(dates, values, 'r')
#		  plt.axis(dates)
		plt.ylabel(self.secs.find_stock(stock))
		plt.xlabel('Date')
		plt.show()
	def new_split(self):
		print('Security',)
		stock = input()
		last_unsplit_date, suggested_ratio = self.prices.find_split_date(self.secs.find_stock(stock))
		print('Last unsplit date [' + last_unsplit_date + ']',)
		split_date = input()
		if split_date == '':
			split_date = last_unsplit_date
		print('Split ratio [' + str(suggested_ratio) + '] for one existing stock')
		ratio = input()
		if ratio == '':
			ratio = suggested_ratio
		dates, values = self.prices.get_dates_and_prices(self.secs.find_stock(stock), None, split_date)
		print(dates)
		print('Update all security prices starting ' + last_unsplit_date + ' into all past available; price is divided by ' + str(ratio))
		input()
		for i in range(len(dates)):
			self.prices.update(self.secs.find_stock(stock), dates[i], values[i]/float(ratio)) 

	def edit_stock(self):
		stock = input('Name of security ')
		stock_obj = self.secs.find_stock(stock, return_obj=True)
		print(stock_obj)
		new_name = input('New name (empty for no change) ')
		if new_name == '':
			new_name = stock_obj.name
		new_aliases = input('New Aliases (empty for no change) ').split(',')
		if new_aliases == '':
			new_aliases = stock_obj.aliases
		for num in range(len(new_aliases)):
			new_aliases[num] = new_aliases[num].strip()
		new_id = input('New id (empty for no change) ')
		if new_id== '':
			new_id = stock_obj.yahoo_id
		new_type = input('New Type (empty for no change) ')
		if new_type == '':
			new_type = stock_obj.type
		self.secs.change_stock(stock_obj.yahoo_id, Security(new_name, new_aliases, new_id, new_type))
	def delete_stock(self):
		stock = input('Name of security ')
		stock_obj = self.secs.find_stock(stock, return_obj=True)
		print(stock_obj)
		do_delete = input('Delete stock ')
		if do_delete.lower() == 'yes':
			self.prices.delete_prices(stock_obj.yahoo_id)
			self.secs.delete_stock(stock_obj.yahoo_id)			  
	def profitability(self):
		portfolio = input('Portfolio [All] ')
		if portfolio == '':
			portfolio = 'All'
		tmp_default = (datetime.date.today() - datetime.timedelta(days=31)).strftime('%Y-%m-%d')
		from_date = input('Start date [' + tmp_default + '] ')
		if from_date == '':
			from_date = tmp_default
		from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
		tmp_default = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
		to_date = input('End date [' + tmp_default + '] ')
		if to_date == '':
			to_date = tmp_default
		to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
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
	def list_portfolio(self):
		portfolio = input('Portfolio [All] ')
		if portfolio == '':
			portfolio = 'All'
		tmp_default = datetime.date.today().strftime('%Y-%m-%d')
		my_date = input('Date of state [' + tmp_default + '] ')
		if my_date == '':
			my_date = tmp_default
		my_date = datetime.datetime.strptime(my_date, "%Y-%m-%d").date()
		stocks = self.transaction.get_portfolio('All', my_date.strftime("%Y-%m-%d"))
#		  print(stocks)
		keys = ['Name', 'Nominal', 'Price', 'Value']		
		x = PrettyTable(keys)
		x.padding_width = 1 # One space between column edges and contents (default)
		prices = []
		tmp = 0.0
		for key in stocks.keys():
			price = self.prices.get_price(key, my_date.strftime("%Y-%m-%d"))
			value = 0.0
			if price != None:
				value = stocks[key] * price
			else:
				print('Price for ' + self.secs.get_name_from_stock_id(key) + ' missing; assuming zero')
			x.add_row([self.secs.get_name_from_stock_id(key), stocks[key], price, value])
			tmp += value
		x.add_row(4*['====='])
		x.add_row(['Total', '----', '----', tmp])
		print(str(x))
	def print_portfolio(self):
		print(self.portfolio)
	def list_portfolio_contents(self):
		print(self.portfolio)
		self.list_content()
	def securities_menu(self, inp=''):
		return self.new_menu(
			[	'List securities',
				'New security',
				'Edit security',
				'Merge security',
				'Delete security',
				'Update security prices',
				'Initialize quotes for last 15 years',
				'New graph',
				'Stock split'],
			[	self.list_stocks,
				self.new_stock,
				self.edit_stock,
				self.merge_stock,
				self.delete_stock,
				self.update_stocks,
				self.get_historic_quotes,
				self.new_graph,
				self.new_split], inp)
	def analyzes_menu(self, inp=''):
		return self.new_menu(
			[	'List portfolio',
				'Profitability'],
			[	self.list_portfolio,
				self.profitability], inp)
	def settings_menu(self, inp=''):
		return self.new_menu(
			[	'Planned saving (p.m.)'],
			[	None], inp)
	def portfolio_menu(self, inp=''):
		return self.new_menu(
			[	'Add portfolio',
				'List portfolios',
				'List content of portfolio'],
			[	self.new_portfolio,
				self.print_portfolio,
				self.list_portfolio_contents], inp)
	def main_menu(self):
		self.new_menu(
			[	'Analyzes - Menu',
				'Securities - Menu',
				'Portfolios - Menu',
				'New transaction',
				'Import from PDFs',
				'Settings (eg. planned savings) - Menu',
				'Forecast'],
			[	self.analyzes_menu,
				self.securities_menu,
				self.portfolio_menu,
				self.new_transaction,
				self.import_pdfs,
				self.settings_menu,
				None])
	def new_menu(self, choices, functions, inp=''):
		letters = 'abcdefghijklmnoprstuvwxyz'
		while True:
			x = PrettyTable(["Key", "Item"])
			x.align["Item"] = "l"
			x.padding_width = 1 # One space between column edges and contents (default)
			for num, choice in enumerate(choices):
				x.add_row([letters[num], choice])
#				  i[1] = i[1].replace(' - Menu', '')
			x.add_row(["-", '---'])
			x.add_row(["q", "Exit"])
			print(x)
			if inp == '':
				try:
					inp = input().lower()
				except KeyboardInterrupt:
					inp = 'q'
			key = inp[:1]
			inp = inp[1:]
			found = False
			for num, choice in enumerate(choices):
				if key == letters[num]:
					found = True
					if choice.find(' - Menu') != -1:
						functions[num](inp)
					else:
						functions[num]()
					break
			if not found and key == 'q':
				break
		return inp		  
	def import_pdfs(self):
		base_path = os.path.expanduser('~') + '/Desktop/PDFs'
		print(base_path)
		for file in os.listdir(base_path):
			if (file.startswith('HV-BEGLEIT') or
				file.startswith('KONTOABSCH') or
				file.startswith('KONTOAUSZU') or
				file.startswith('PERSONAL_I') or
				file.startswith('TERMINANSC') or
				file.startswith('WICHTIGE_M') or
				file.startswith('VERLUSTVER') or
				file.startswith('VERTRAGSRE')):
				# Remove invalid PDFs
				print('Ignore ' + file)
				os.remove(base_path + '/' + file)
			elif file.endswith('.pdf'):
				print('Import ' + file)
				data = self.transaction.get_data_from_text(subprocess.check_output(['/usr/local/bin/pdf2txt.py', base_path + '/' + file]).decode("utf-8"))
				if data != None:
					print(data['name'])
					if self.secs.find_stock(data['name']) == None:
						# Add security as dummy if not already existing
						self.secs.add(data['name'], '', 'unknown', 'unkown')
					if data['type'] in ['b', 's']:
						if not self.transaction.add(data['type'], self.secs.get_stock_id_from_yahoo_id(self.secs.find_stock(data['name'])), data['date'], data['nominale'], data['value'], data['cost'], 'All'):
							print(data['name'] +': could not add transaction (e.g. security not available)')
							
						else:
							print('Transaction successful')
							# Remove successful PDFs
							os.remove(base_path + '/' + file)

					elif data['type'] in ['d']:
						if not self.transaction.add(data['type'], self.secs.get_stock_id_from_yahoo_id(self.secs.find_stock(data['name'])), data['date'], 0, data['value'], 0, 'All'):
							print(data['name'] +': could not add transaction (e.g. security not available)')
						else:
							print('Transaction successful')
							# Remove successful PDFs
							os.remove(base_path + '/' + file)
				else:
					# Remove invalid PDFs
					os.remove(base_path + '/' + file)
	def new_transaction(self):
		print('Transaction type (Buy/Sell/Dividend)')
		type = input()
		print('Security')
		stock = input()

		portfolio = input('Portfolio [All] ')
		if portfolio == '':
			portfolio = 'All'

		tmp_default = datetime.date.today().strftime('%Y-%m-%d')
		print('Date [' + tmp_default + ']')
		date = input()
		if date == '':
			date = tmp_default
		print('Nominale')
		nom = float(input())
		print('Price')
		price = float(input())
		print('Cost')
		cost = float(input())
		self.transaction.add(type, self.secs.get_stock_id_from_yahoo_id(self.secs.find_stock(stock)), date, nom, price, cost, portfolio)