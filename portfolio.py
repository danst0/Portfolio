#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
from prettytable import PrettyTable
import sys
#from stockquotes import GoogleFinanceAPI
from pprint import pprint
import ystockquote
import urllib
import datetime
import re
import pdb
import sqlite3

class Analyses:
    """Perform additional analyses on the Portfolios and stocks."""
    pass
    
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('data.sql', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        # Create tables    
        try:
            self.c.execute('''CREATE TABLE stocks (id INTEGER PRIMARY KEY, name TEXT, yahoo_id TEXT, type TEXT)''')
        except:
            pass
        else:
            print('Creating table for stocks')
        try:
            self.c.execute('''CREATE TABLE prices (id INTEGER PRIMARY KEY, stock_id INTEGER, date TEXT, price REAL)''')
        except:
            pass
        else:
            print('Creating table for prices')


    def close(self):
        self.conn.commit()
        self.conn.close()
class Portfolio:
    """Collection of different portfolios or stocks."""
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.children = []
    def add(self, parent, name):
        if self.name == parent:
            self.children.append(Portfolio(name, parent))
        else:
            for i in self.children:
                i.add(parent, name)
    def __str__(self, level=1):
        output = self.name + '\n'
        for i in self.children:
            output += '    '*level + '+-- ' + i.__str__(level+1)
        return output
        

class Security:
    """Class for stocks, bond, cash, everything is a security."""
    def __init__(self, name, yahoo_id, type):
        self.name = name
        self.yahoo_id = yahoo_id
        self.type = type
    def list(self):
        return (self.name, self.yahoo_id, self.type)
    def __str__(self):
        return ' '.join(self.list())

class Securities:
    """Wrapper for all stored securities"""
    keys = ['Name', 'ID', 'Type', 'Last price']
    def __init__(self, data, prices):
        self.data = data
        try:
            self.securities = pickle.load( open( "securities.p", "rb" ) )
        except:
            self.securities = []
        self.prices = prices

    def add(self, *args):
        self.securities.append(Security(*args))
        pickle.dump( self.securities, open( "securities.p", "wb" ) )
    def empty(self):
        return False if len(self.securities) > 0 else True
    def __str__(self):
        x = PrettyTable(self.keys)
        x.align[self.keys[0]] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in self.securities:
            x.add_row(i.list() + (self.prices.get_last_price(i.id),))
        return str(x)
    def __iter__(self):
        for x in self.securities:
            yield x
        
class Transaction:
    """Class to store transactions"""
    def __init__(self, id, date, nominal, price, cost):
        self.id = id
        self.date = date
        # number of stocks/nominale
        self.nominal = nominal
        self.price = price
        self.cost = cost
    
    

class Prices:
    """Class to store price developments."""
    numbers = {}
    def __init__(self, data):
        self.data = data
        for line in self.data.c.execute('SELECT * FROM stocks'):
            print(line)

    def update(self,id, date, price):
#         pdb.set_trace()
        print(id, date, price)
        if id not in self.numbers.keys():
            self.numbers[id] = {}
        self.numbers[id][date] = price
        c.executemany('INSERT INTO prices VALUES (?,?,?)', (id, date, price))
        pickle.dump(self.numbers, open('numbers.p', 'wb'))
    def get_price(self, id, date):
        price = None
        try:
            price = self.numbers[id][date]
        except:
            pass
        return price
    
    def get_prices(self, id):
        prices = None
        try:
            prices = self.numbers[id]
        except:
            pass
        return prices
    def get_last_price(self, id):
        prices = self.get_prices(id)
        max_key = max(prices, key=prices.get)
        return prices[max_key]
    def get_quote(self,symbol):
        base_url = 'http://finance.google.com/finance?q='
        content = str(urllib.request.urlopen(base_url + symbol).read())
        m = re.search('id="ref_694653_l".*?>(.*?)<', content)
        if m:
            quote = m.group(1)
        else:
            quote = 'no quote available for: ' + symbol
        return quote
class UI:
    """Class to display user interface."""
    def __init__(self, securities, portfolio, prices):
        self.secs = securities
        self.portfolio = portfolio
        self.prices = prices
        self.last_update = datetime.datetime.now() + datetime.timedelta(days=-1)
        while True:
            self.main_menu()
            try:
                inp = input().lower()
            except KeyboardInterrupt:
                inp = 'q'
#                 sys.exit()
#             print(inp)
            for key in inp:
#                 print(key)
                if key == 's':
                    self.new_stock()
                elif key == 'p':
                    self.new_portfolio()
                elif key == 'l':
                    self.list_stocks()
                elif key == 'u':
                    self.update_stocks()
                    pprint(self.prices.numbers)
                elif key == 'q':
                    sys.exit()
    def menu(self, items):
        x = PrettyTable(["Key", "Item"])
        x.align["Item"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in items:
            x.add_row(i)
        print(x)
    def update_stocks(self):
        now = datetime.datetime.now()
#         print(now, self.last_update)
        if now < self.last_update + datetime.timedelta(seconds=30):
            print('Please leave at least 30 secs between each update.')
            return
        else:
            self.last_update = now
        today = datetime.date.today()
        if today.weekday() >= 5:
            today = today + datetime.timedelta(days=4-today.weekday())
        day_str = today.strftime('%Y-%m-%d')
#         print(day_str)
        
        for sec in self.secs:
#             print(sec.name, sec.id)
            quote = None
#             quote = self.prices.get_quote('goog')
#             print(quote)
            try:
                quote = ystockquote.get_historical_prices(sec.id, day_str, day_str)
            except urllib.error.HTTPError:
                print('No quotes found for:', sec.name)
            else:
#                 print(quote)
                self.prices.update(sec.id, day_str, quote[day_str]['Close'])
    def list_stocks(self):
        if not self.secs.empty():
            print(self.secs)
        else:
            print('No stocks in database.')
    def new_stock(self):
        print('Name ',) 
        name = input()
        print ('ID ',)
        id = input()
        print ('Type ',)
        type = input()
        self.secs.add(name, id, type)

    def new_portfolio(self):
        print(self.portfolio)
        print('Parent ',) 
        parent = input()
        
        print('Name ',) 
        name = input()

        self.portfolio.add(parent, name)
        
    def main_menu(self):
        menu = []
        menu.append(["s", "New security"])
        menu.append(["p", "Add portfolio"])
        menu.append(["t", "New transaction"])
        menu.append(["l", "List stocks in portfolio"])
        menu.append(['s', 'Settings (eg. planned savings)'])
        menu.append(['f', 'Forecast'])
        menu.append(['u', 'Update stock prices'])
        menu.append(["-", '---'])
        menu.append(["q", "Quit"])
        self.menu(menu)
    
if __name__ == "__main__":
    DATA = Database()
    try:
        PORTFOLIO = pickle.load(open('portfolio.p', 'rb'))
    except:
        PORTFOLIO = Portfolio('All')
#     print(str(PORTFOLIO).strip('\n'))
    PRICES = Prices(DATA)
    SECS = Securities(DATA, PRICES)
    UI = UI(SECS, PORTFOLIO, PRICES)
    print(SECS)
    pickle.dump( PORTFOLIO, open('portfolio.p', 'wb'))
    DATA.close()
