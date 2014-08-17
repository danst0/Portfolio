#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable
import os
import subprocess
import urllib
import ystockquote
from Securities import Security
from input_methods import *
from helper_functions import *
import matplotlib.pyplot as plt
import sys
import codecs

class UI:
	"""Class to display user interface."""
	def __init__(self, securities, portfolio, prices, transaction, money):
		self.secs = securities
		self.portfolio = portfolio
		self.prices = prices
		self.transaction = transaction
		self.money = money
		self.last_update = datetime.datetime.now() + datetime.timedelta(days=-1)
		go_on = True
		while go_on:
			go_on = self.main_menu()
		random.seed()

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
			if sec.yahoo_id != '' and not sec.yahoo_id.startswith('unknown'):
				print('Updating', sec.yahoo_id)
				quote = None
				try:
					quote = ystockquote.get_historical_prices(sec.yahoo_id, first_day_str, today_str)
				except urllib.error.HTTPError:
					print('No quotes found for:', sec.name)
					self.last_update += datetime.timedelta(seconds=-90)
				else:
#					  print(quote)
					for key in quote:
						self.prices.update(sec.isin_id, key, quote[key]['Close'])
			else:
				print('No Yahoo ID for', sec.name)
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
			if not sec.isin_id.startswith('unknown'):
				quote = None
				quote = self.prices.get_quote(sec.isin_id)
				if not quote:
					print('No quotes found for:', sec.name)
					self.last_update += datetime.timedelta(seconds=-30)
				else:
					self.prices.update(sec.isin_id, day_str, quote)
			else:
				print('No ISIN for', sec.name)
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
		rand_id = 'unknown'+rand_str()
		isin_id = input_string('ISIN', '[A-Z]{2}[0-9]{10}', rand_id)
		yahoo_id = input_string('Yahoo ID', '[A-Z0-9]{1,10}', rand_id)
		type = input_string('Type', 'Stock|Bond|REIT')
		self.secs.add(name, aliases, isin_id, yahoo_id, type)
	def list_content(self):

		pf = input('Portfolio [All] ')
		if pf == '':
			pf = 'All'
		transactions = self.transaction.get_total_for_portfolio(pf)
#		  print(transactions)
		
		x = PrettyTable(['Name', 'Nominal', 'Cost', 'Value'])
		x.align['Invested'] = "l" # Left align city names
		x.padding_width = 1 # One space between column edges and contents (default)
#		  print(transactions)
		for i in sorted(transactions, key=lambda x: x[0].lower()):
#			  print(i)
			x.add_row(i[:-1] + (self.prices.get_last_price(i[0], none_equals_zero=True) * i[1],))
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
#		print(dates)
#		print('Update all security prices starting ' + last_unsplit_date + ' into all past available; price is divided by ' + str(ratio))
#		print('Please manually add a corresponding transaction to internalize the value reduction in the stock nominale.')
		go_on = input_yes('Update all security prices starting ' + last_unsplit_date + ' into all past available; price is divided by ' + str(ratio))
		if go_on:
			print('Changing prices')
			for i in range(len(dates)):
				self.prices.update(self.secs.find_stock(stock), dates[i], values[i]/float(ratio))
			stocks_at_split = self.transaction.get_portfolio('All', split_date)
			stock_id = self.secs.get_stock_id_from_isin_id(self.secs.find_stock(stock))
			number_before_split = stocks_at_split[stock_id]
#			print(stocks_at_split)
#			print(stock_id)
	#		print(number_before_split)
			number_after_split = number_before_split * ratio
			date_after_split = (datetime.datetime.strptime(split_date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
			print('Adding additional stocks')
			self.transaction.add('b', stock_id, date_after_split, number_after_split - number_before_split, 0.0, 0.0, 'All')

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
		new_isin_id = input('New ISIN (empty for no change) ')
		if new_isin_id== '':
			new_isin_id = stock_obj.isin_id
		new_id = input('New yahoo id (empty for no change) ')
		if new_id== '':
			new_id = stock_obj.yahoo_id
		new_type = input('New Type (empty for no change) ')
		if new_type == '':
			new_type = stock_obj.type
		self.secs.change_stock(stock_obj.isin_id, Security(new_name, new_aliases, new_isin_id, new_id, new_type))
	def delete_stock(self):
		stock = input('Name of security ')
		stock_obj = self.secs.find_stock(stock, return_obj=True)
		print(stock_obj)
		do_delete = input('Delete stock ')
		if do_delete.lower() == 'yes':
			self.prices.delete_prices(stock_obj.isin_id)
			self.secs.delete_stock(stock_obj.isin_id)			  
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
#		print(stocks_at_start)
		print('Portfolio at start date', from_date.strftime("%Y-%m-%d"))
		self.portfolio.list_pf(from_date)
		print('Portfolio at end date', to_date.strftime("%Y-%m-%d"))
		self.portfolio.list_pf(to_date)
		portfolio_value_at_start = 0.0
		for key in stocks_at_start.keys():
			portfolio_value_at_start += stocks_at_start[key] * self.prices.get_last_price_from_stock_id(key, from_date.strftime("%Y-%m-%d"), none_equals_zero=True)
		stocks_at_end = self.transaction.get_portfolio('All', to_date.strftime("%Y-%m-%d"))
		portfolio_value_at_end = 0.0
		for key in stocks_at_end.keys():
			portfolio_value_at_end += stocks_at_end[key] * self.prices.get_last_price_from_stock_id(key, to_date.strftime("%Y-%m-%d"), none_equals_zero=True)

		invest = self.transaction.get_total_invest('All', from_date, to_date)
		divest = self.transaction.get_total_divest('All', from_date, to_date)
		dividend = self.transaction.get_total_dividend('All', from_date, to_date)

		profit_incl_on_books = portfolio_value_at_end + invest - divest - portfolio_value_at_start + dividend
		print('Absolute KPIs')
		keys = ['Start portfolio', 'Investment', 'Divestment', 'Current portfolio', 'Dividend', 'Profit (incl. on books)']
		x = PrettyTable(keys)
		x.padding_width = 1 # One space between column edges and contents (default)
		x.add_row([nice_number(portfolio_value_at_start), nice_number(-invest), nice_number(divest), nice_number(portfolio_value_at_end), nice_number(dividend), nice_number(profit_incl_on_books)])
		print(str(x))
		print('Relative KPIs')		  
		keys = ['ROI']
		x = PrettyTable(keys)
		x.padding_width = 1 # One space between column edges and contents (default)
		if portfolio_value_at_start - invest != 0:
			tmp = [nice_number(100 * profit_incl_on_books/(portfolio_value_at_start - invest)) + '%']
		else:
			tmp = ['n/a']
		x.add_row(tmp)
		print(str(x))
		
	def last_day_of_last_month(self, date):
		return date.replace(day=1) - datetime.timedelta(days=1)
		
	def cash_info(self):
		tmp_default = self.last_day_of_last_month(datetime.date.today()).strftime('%Y-%m-%d')
		my_date = input('Date of state [' + tmp_default + '] ')
		if my_date == '':
			my_date = tmp_default
		my_income = input('Income in month ')
		my_total = input('Total cash at hand (w/o portfolios) ')
		self.money.add_income(my_date, my_income)
		self.money.add_total(my_date, my_total)

	def list_portfolio(self):
		portfolio = input('Portfolio [All] ')
		if portfolio == '':
			portfolio = 'All'
		tmp_default = datetime.date.today().strftime('%Y-%m-%d')
		my_date = input('Date of state [' + tmp_default + '] ')
		if my_date == '':
			my_date = tmp_default
		my_date = datetime.datetime.strptime(my_date, "%Y-%m-%d").date()
		self.portfolio.print_pf(my_date)
	def print_portfolio(self):
		print(self.portfolio)
	def list_portfolio_contents(self):
		print(self.portfolio)
		self.list_content()
	def merge_stock(self):
		first_stock = input('Remaining security ')
		stock_obj = self.secs.find_stock(first_stock, return_obj=True)
		main_isin = self.secs.find_stock(first_stock)
		print(stock_obj)
		second_stock = input('Vanishing security ')
		stock_obj = self.secs.find_stock(second_stock, return_obj=True)
		secondary_isin = self.secs.find_stock(second_stock)
		print(stock_obj)
		self.secs.merge_stocks_from_isin(main_isin, secondary_isin)
		
		
	def manual_price_update(self):
		stock = input('Security ')
		print(self.secs.find_stock(stock))
		tmp_default = (datetime.date.today()).strftime('%Y-%m-%d')
		my_date = input('Price date [' + tmp_default + '] ')
		if my_date == '':
			my_date = tmp_default
		my_date = datetime.datetime.strptime(my_date, "%Y-%m-%d").date()
		price = input_float('Price')
		self.prices.update(self.secs.find_stock(stock), my_date, price)
	def savings(self):
		tmp_default = self.last_day_of_last_month(datetime.date.today() - relativedelta(months=1)).strftime('%Y-%m-%d')
		from_date = input('From date [' + tmp_default + '] ')
		if from_date == '':
			from_date = tmp_default
		tmp_default = self.last_day_of_last_month(datetime.date.today()).strftime('%Y-%m-%d')
		to_date = input('To date [' + tmp_default + '] ')
		if to_date == '':
			to_date = tmp_default
		self.money.get_all(from_date, to_date)
	def securities_menu(self, inp=''):
		return self.new_menu(
			[	'List securities',
				'New security',
				'Edit security',
				'Merge security',
				'Delete security',
				'Update security prices',
				'Manual price update',
				'Initialize quotes for last 15 years',
				'New graph',
				'Stock split'],
			[	self.list_stocks,
				self.new_stock,
				self.edit_stock,
				self.merge_stock,
				self.delete_stock,
				self.update_stocks,
				self.manual_price_update,
				self.get_historic_quotes,
				self.new_graph,
				self.new_split], inp)
	def analyzes_menu(self, inp=''):
		return self.new_menu(
			[	'List portfolio',
				'Saving development',
				'Profitability'],
			[	self.list_portfolio,
				self.savings,
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
				'Add cash info', 
				'Import from PDFs',
				'Settings (eg. planned savings) - Menu',
				'Forecast'],
			[	self.analyzes_menu,
				self.securities_menu,
				self.portfolio_menu,
				self.new_transaction,
				self.cash_info,
				self.import_pdfs,
				self.settings_menu,
				None])
	def highligh_first_letter(self, text, letter):
		pos = text.lower().find(letter)
		return text[:pos] + '[' + text[pos:pos+1] + ']' + text[pos+1:]
	def new_menu(self, choices, functions, inp=''):
		while True:
			letters = ''
			for choice in choices:
				for i in range(len(choice)):
#					print(choice[i], letters)
					if choice[i].lower() not in letters and choice[i].lower() != 'q':
						letters += choice[i].lower()
						break
			letters += 'q'
#			print(letters)	  
			x = PrettyTable(["Key", "Item"])
			x.align["Item"] = "l"
			x.padding_width = 1 # One space between column edges and contents (default)
			for num, choice in enumerate(choices):
				x.add_row([letters[num], self.highligh_first_letter(choice, letters[num])])
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
						inp = functions[num](inp)
					else:
						functions[num]()
					break
			if not found and key == 'q':
				break
		return inp
	def import_pdfs(self):
		base_path = os.path.expanduser('~') + '/Desktop/PDFs'
		print(base_path)
		file_counter = 0
		for file in os.listdir(base_path):
			if file.startswith('PERSONAL') and file.endswith('.pdf'):
				print('Import ' + file)
				subprocess.check_output(['/usr/local/bin/pdftotext', '-nopgbrk', '-eol', 'mac', '-table', base_path + '/' + file, base_path + '/data.txt'])
				with open(base_path + 'data.txt', 'rb') as myfile:
					data = myfile.read()
#				print(data)
				data = self.transaction.get_data_from_personal_investment_report(data)
				if data:
					for name, date, price in data:
						print('Updated prices', name, date, price)
						date = datetime.datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')
						self.prices.update(self.secs.find_stock(name), date, price, interactive=True, alt_name=name)
					file_counter += 1

#				os.remove(base_path + '/' + file)
				sys.exit()
		for file in os.listdir(base_path):
			if (file.startswith('HV-BEGLEIT') or
				file.startswith('KONTOABSCH') or
				file.startswith('KONTOAUSZU') or
				file.startswith('PERSONAL') or
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
						tmp_id = 'unknown'+rand_str()
						self.secs.add(data['name'], '', tmp_id, tmp_id , 'unkown', interactive=True)
					if data['type'] in ['b', 's']:
						if not self.transaction.add(data['type'], self.secs.get_stock_id_from_isin_id(self.secs.find_stock(data['name'])), data['date'], data['nominale'], data['value'], data['cost'], 'All'):
							print(data['name'] +': could not add transaction (e.g. security not available)')
						else:
							print('Transaction successful')
							file_counter += 1
							# Remove successful PDFs
							os.remove(base_path + '/' + file)

					elif data['type'] in ['d']:
						if not self.transaction.add(data['type'], self.secs.get_stock_id_from_isin_id(self.secs.find_stock(data['name'])), data['date'], 0, data['value'], 0, 'All'):
							print(data['name'] +': could not add transaction (e.g. security not available)')
						else:
							print('Transaction successful')
							file_counter += 1
							# Remove successful PDFs
							os.remove(base_path + '/' + file)
				else:
					# Remove invalid PDFs
					os.remove(base_path + '/' + file)
		print(file_counter, 'files successfully imported.')
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
		nom = input_float('Nominale')
		price = input_float('Price')
		cost = input_float('Cost')
		self.transaction.add(type, self.secs.get_stock_id_from_isin_id(self.secs.find_stock(stock)), date, nom, price, cost, portfolio)