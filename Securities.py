#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prettytable import PrettyTable
import string
import uuid

def normalize(s):
	for p in string.punctuation:
		s = s.replace(p, '')
	return s.lower().strip() 
		
class Security:
	"""Class for stocks, bond, cash, everything is a security."""
	def __init__(self, name, aliases, isin_id, yahoo_id, type):
		self.name = name
		if isin_id == None:
			isin_id = ''
		self.isin_id = isin_id
		if yahoo_id == None:
			yahoo_id = ''
		self.yahoo_id = yahoo_id
		self.type = type
		# Aliases should be a list!!
		if aliases == None or aliases == '':
			self.aliases = []
		else:
			self.aliases = aliases
			if aliases != '' and '' in self.aliases:
				self.aliases.remove('')		
		self.keys = ['Name', 'Aliases', 'ISIN', 'Yahoo-ID', 'Type']
	def list(self):
		return (self.name, ', '.join(self.aliases), self.isin_id, self.yahoo_id, self.type)
	def __str__(self):
		x = PrettyTable(self.keys)
		x.align[self.keys[0]] = "l" # Left align city names
		x.padding_width = 1 # One space between column edges and contents (default)
		x.add_row(self.list())
		return str(x)

class Securities:
	"""Wrapper for all stored securities"""
	keys = ['Name', 'Aliases', 'ISIN', 'Yahoo ID', 'Type', 'Last price']
	def __init__(self, data):
		self.data = data
		self.securities = []
		all = self.data.c.execute('SELECT name, aliases, isin_id, yahoo_id, type FROM stocks')
		for line in all.fetchall():
			line = list(line)
#			  print(line)
			if line[1] != None:
				line[1] = line[1].split('::')
			self.securities.append(Security(*line))
		self.prices = None

	def add(self, name, aliases, isin_id, yahoo_id, type, interactive=False):
#		  print(aliases)
		already_exists = False
		for sec in self.securities:
			if (normalize(sec.isin_id) == normalize(isin_id)
				and normalize(isin_id)[:7] != normalize('unknown')):
				already_exists = True
				break
		if not already_exists:
#			print(aliases)
			if aliases != '' and '' in aliases :
				aliases.remove('')
			new_sec = Security(name, aliases, isin_id, yahoo_id, type)	
			interactive_success = False
			if interactive:
				print(self)
				print('Adding the following security')
				print(new_sec)
				alternative = input('Is there an alternative? If yes, input name here else just hit enter? ')
				if alternative != '':
					tmp_sec = self.find_stock(alternative, return_obj=True)
					tmp_sec.aliases = tmp_sec.aliases + [new_sec.name]
					self.change_stock(tmp_sec.isin_id, tmp_sec)
					interactive_success = True
			if not interactive_success:
    			self.securities.append(new_sec)
	    		self.data.c.execute('INSERT INTO stocks(id, name, aliases, isin_id, yahoo_id, type) VALUES (?, ?, ?, ?, ?, ?)', (uuid.uuid4(), name, '::'.join(aliases), isin_id, yahoo_id, type))
		else:
			print('ID for Stock already exists, therefore not added')
	def change_stock(self, isin_id, sec):
		found = False
		for num, item in enumerate(self.securities):
			if isin_id.lower() in item.isin_id.lower():
				found = True
				self.securities[num] = sec
#				print('UPDATE stocks set name = ?, aliases = ?, isin_id = ?, yahoo_id = ?, type = ? WHERE isin_id = ?', (sec.name, '::'.join(sec.aliases), isin_id, sec.yahoo_id, sec.type, isin_id))
				self.data.c.execute('UPDATE stocks set name = ?, aliases = ?, isin_id = ?, yahoo_id = ?, type = ? WHERE isin_id = ?', (sec.name, '::'.join(sec.aliases), isin_id, sec.yahoo_id, sec.type, isin_id))
				self.data.commit()
				break
		return found
	def delete_stock(self, isin_id):
		found = False
		for num, item in enumerate(self.securities):
			if isin_id.lower() in item.isin_id.lower():
				found = True
				tmp = self.securities.pop(num)
				self.data.c.execute('DELETE FROM stocks WHERE isin_id = ? AND name = ?', (isin_id, tmp.name))
				break
		return found	  
#		  pickle.dump( self.securities, open( "securities.p", "wb" ) )
	def empty(self):
		return False if len(self.securities) > 0 else True
	def get_name_from_stock_id(self, stock_id):
		name = self.data.c.execute('''SELECT name FROM stocks WHERE id = ?''', (stock_id,)).fetchone()
		return None if name is None else name[0]
	def get_isin_id_from_stock_id(self, stock_id):
		name = self.data.c.execute('''SELECT isin_id FROM stocks WHERE id = ?''', (stock_id,)).fetchone()
		return None if name is None else name[0]

	def merge_stocks_from_isin(self, main_isin, secondary_isin):
		main_stock = self.find_stock(main_isin, return_obj=True)
		secondary_stock = self.find_stock(secondary_isin, return_obj=True)
		new_name = main_stock.name
		new_aliases = main_stock.aliases + secondary_stock.aliases + [secondary_stock.name]
		new_isin = main_stock.isin_id
		if main_stock.isin_id.startswith('unknown') and not secondary_stock.isin_id.startswith('unknown'):
			new_isin = secondary_stock.isin
		new_yahoo_id = main_stock.yahoo_id
		if main_stock.yahoo_id.startswith('unknown') and not secondary_stock.yahoo_id.startswith('unknown'):
			new_yahoo_id = secondary_stock.yahoo_id
		new_type = main_stock.type
		if main_stock.type == None and not secondary_stock.type == None:
			new_type = secondary_stock.type
		yes_no = input('Should I do the merge?')
		if yes_no == 'yes':
			self.data.c.execute('''UPDATE transactions SET stock_id = ? WHERE stock_id = ?''', (self.get_stock_id_from_isin_id(main_isin), self.get_stock_id_from_isin_id(secondary_isin)))
			self.change_stock(main_isin, Security(new_name, new_aliases, new_isin, new_yahoo_id, new_type))
			self.delete_stock(secondary_isin)
			self.prices.delete_prices(secondary_isin)
			
		
		

	def __str__(self):
		x = PrettyTable(self.keys)
		x.align[self.keys[0]] = "l" # Left align city names
		x.padding_width = 1 # One space between column edges and contents (default)
		for i in self.securities:
#			print(i.isin_id, self.prices.get_last_price(i.isin_id))
			x.add_row(i.list() + (self.prices.get_last_price(i.isin_id),))
		return str(x)
	def __iter__(self):
		for x in self.securities:
			yield x
	def find_stock(self, stock_id_or_name, return_obj=False):
		"""Return ISIN or stock object"""
		found = None
		found_obj = None
		for item in self.securities:
			if (normalize(stock_id_or_name) in normalize(item.name) or
				normalize(stock_id_or_name) in normalize(item.isin_id)):
				found = item.isin_id
				found_obj = item
				break
			else:
				for alias in item.aliases:
					if normalize(stock_id_or_name) == normalize(alias):
						found = item.isin_id
						found_obj = item
						break						 
		if return_obj:
			return found_obj
		else:
			return found
	def get_stock_id_from_isin_id(self, isin_id):
		stock_id = self.data.c.execute('''SELECT id FROM stocks WHERE isin_id = ?''', (isin_id,)).fetchone()
		return None if stock_id is None else stock_id[0]