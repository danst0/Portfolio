#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import this
import pickle
from prettytable import PrettyTable
import sys, os
#from stockquotes import GoogleFinanceAPI
from pprint import pprint
import ystockquote
import urllib
import datetime
import re
import pdb
import uuid
import subprocess
import string
from Database import Database
from Portfolio import Portfolio
from Securities import Securities
from Securities import Security
from Transaction import Transaction
from Prices import Prices
from UI import UI

import matplotlib.pyplot as plt
# Sample stocks		   
# +--------------------+---------+-------+------------+
# | Name			   |	ID	 |	Type | Last price |
# +--------------------+---------+-------+------------+
# | Aareal Bank AG	   |  ARL.DE | Stock |	 32.25	  |
# | Apple Inc.		   |  APC.F	 | Stock |	  72.5	  |
# | Host Marriot	   |  HMT.F	 |	REIT |	 16.72	  |
# | DB TR EU Renten 1C | DBXN.DE |	Bond |	 209.37	  |
# | DB MSCI EU M 1C	   | DX2I.DE | Stock |	  73.7	  |
# +--------------------+---------+-------+------------+

# Next todo: get price from specific date, multiply by number of stocks


def normalize(s):
	for p in string.punctuation:
		s = s.replace(p, '')
	return s.lower().strip() 

class Analyses:
	"""Perform additional analyses on the Portfolios and stocks."""
	pass


	
if __name__ == "__main__":
	DATA = Database()
	try:
		PORTFOLIO = pickle.load(open('portfolio.p', 'rb'))
	except:
		PORTFOLIO = Portfolio('All')
	PRICES = Prices(DATA)
	SECS = Securities(DATA)
	PRICES.secs = SECS
	SECS.prices = PRICES
#	  print('PRICES')
#	  print(PRICES)
	print('SECS')
	print(SECS)
	TRANSACTION = Transaction(DATA)
	UI = UI(SECS, PORTFOLIO, PRICES, TRANSACTION)
	pickle.dump( PORTFOLIO, open('portfolio.p', 'wb'))
#	  print('PRICES')
#	  print(PRICES)
	print('SECS')
	print(SECS)
	print('TRANSACTIONS')
	print(TRANSACTION)
	DATA.close()
