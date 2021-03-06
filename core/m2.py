#!/usr/bin/env python3
# -*- coding: utf-8 -*-

VERSION = '0.3'

# import this
import pickle
# from stockquotes import GoogleFinanceAPI

import string
from money import Money
from database import Database
from Portfolio import Portfolio
from Securities import Securities
from Transaction import Transaction
from Prices import Prices
from UI import UI



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
    print('pf - Portfolio Version', VERSION)
    DATA = Database()
    PRICES = Prices(DATA)
    SECS = Securities(DATA)
    PRICES.secs = SECS
    SECS.prices = PRICES
    #	  print('PRICES')
    #	  print(PRICES)
    # 	print('SECS')
    print(SECS)
    TRANSACTION = Transaction(DATA, SECS, PRICES)
    PORTFOLIO = Portfolio('All', TRANSACTION, PRICES, SECS)
    MONEY = Money(DATA, PORTFOLIO)
    TRANSACTION.money = MONEY
    UI = UI(SECS, PORTFOLIO, PRICES, TRANSACTION, MONEY)
    pickle.dump(PORTFOLIO, open('portfolio.p', 'wb'))
    #	  print('PRICES')
    #	  print(PRICES)
    #	print('SECS')
    #	print(SECS)
    # 	print('TRANSACTIONS')
    print(TRANSACTION)
    DATA.close()
