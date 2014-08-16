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


import string
from Money import Money
from Database import Database
from Portfolio import Portfolio
from Securities import Securities
from Securities import Security
from Transaction import Transaction
from Prices import Prices
from UI import UI

import matplotlib.pyplot as plt

# Rounding within pretty table
# Verify input of PDF parser

def normalize(s):
	for p in string.punctuation:
		s = s.replace(p, '')
	return s.lower().strip() 

class Analyses:
	"""Perform additional analyses on the Portfolios and stocks."""
	pass

if __name__ == "__main__":
#     print('pf - Portfolio Version 0.3')
	DATA = Database()
	PRICES = Prices(DATA)
	SECS = Securities(DATA)
	PRICES.secs = SECS
	SECS.prices = PRICES
#	  print('PRICES')
#	  print(PRICES)
	print('SECS')
	print(SECS)
	TRANSACTION = Transaction(DATA, SECS, PRICES)
	PORTFOLIO = Portfolio('All', TRANSACTION, PRICES)
	MONEY = Money(DATA, PORTFOLIO)
	TRANSACTION.money = MONEY
	UI = UI(SECS, PORTFOLIO, PRICES, TRANSACTION, MONEY)
	pickle.dump( PORTFOLIO, open('portfolio.p', 'wb'))
#	  print('PRICES')
#	  print(PRICES)
# 	print('SECS')
# 	print(SECS)
	print('TRANSACTIONS')
	print(TRANSACTION)
	DATA.close()
