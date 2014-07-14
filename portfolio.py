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
import matplotlib.pyplot as plt
        

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
            print('Created table for stocks')
        try:
            self.c.execute('''CREATE TABLE prices (id INTEGER PRIMARY KEY, stock_id INTEGER, date TEXT, price REAL)''')
        except:
            pass
        else:
            print('Created table for prices')

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
        self.securities = []
        all = self.data.c.execute('SELECT * FROM stocks')
        for line in all.fetchall():

            self.securities.append(Security(*line[1:]))
#         print(self.securities)
        self.prices = prices

    def add(self, name, yahoo_id, type):
        self.securities.append(Security(name, yahoo_id, type))
        self.data.c.execute('INSERT INTO stocks(name, yahoo_id, type) VALUES (?, ?, ?)', (name, yahoo_id, type))

#         pickle.dump( self.securities, open( "securities.p", "wb" ) )
    def empty(self):
        return False if len(self.securities) > 0 else True
    def __str__(self):
        x = PrettyTable(self.keys)
        x.align[self.keys[0]] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in self.securities:
            x.add_row(i.list() + (self.prices.get_last_price(i.yahoo_id),))
        return str(x)
    def __iter__(self):
        for x in self.securities:
            yield x
    def find_stock(self, stock_id_or_name):
        found = None
        for item  in self.securities:
            if (stock_id_or_name.lower() in item.name.lower() or
                stock_id_or_name.lower() in item.yahoo_id.lower()):
                found = item.yahoo_id
                break
        return found
        
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
    def get_dates_and_prices(self, yahoo_id, from_date, to_date=datetime.date.today().strftime('%Y-%m-%d')):
        stock_id = self.get_stock_id_from_yahoo_id(yahoo_id)
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
    def find_split_date(self, yahoo_id):
        prices = self.get_prices(yahoo_id)
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
    def get_stock_id_from_yahoo_id(self, yahoo_id):
        stock_id = self.data.c.execute('''SELECT id FROM stocks WHERE yahoo_id = ?''', (yahoo_id,)).fetchone()[0]
        return stock_id
    def row_exists(self, stock_id, date):
        result = self.data.c.execute('''SELECT price FROM prices WHERE stock_id = ? AND date = ?''', (stock_id, date)).fetchone()
        return False if result == None else True
    def update(self, yahoo_id, date, price):
        id = self.get_stock_id_from_yahoo_id(yahoo_id)
        if id not in self.numbers.keys():
            self.numbers[id] = {}
        self.numbers[id][date] = price
        if self.row_exists(id, date):
            self.data.c.execute('''UPDATE prices SET price = ? WHERE stock_id = ? AND date = ?''', (price, id, date))
        else:
            self.data.c.execute('''INSERT INTO prices(stock_id, date, price) VALUES (?, ?, ?)''', (id, date, price))
    def get_price(self, id, date):
        price = None
        try:
            price = self.numbers[id][date]
        except:
            pass
        return price
    def get_prices(self, id):
        id = self.get_stock_id_from_yahoo_id(id)
        prices = None
        try:
            prices = self.numbers[id]
        except:
            pass
        return prices
    def get_last_price(self, id):
#         pdb.set_trace()
        prices = self.get_prices(id)
#         print(prices)
        if prices != None:
            max_key = max(prices.keys())
            return prices[max_key]
        else:
            return None
    def get_quote(self,symbol):
        base_url = 'http://finance.google.com/finance?q='
        content = str(urllib.request.urlopen(base_url + symbol).read())
        m = re.search('id="ref_694653_l".*?>(.*?)<', content)
        if m:
            quote = m.group(1)
        else:
            quote = 'no quote available for: ' + symbol
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
class UI:
    """Class to display user interface."""
    def __init__(self, securities, portfolio, prices):
        self.secs = securities
        self.portfolio = portfolio
        self.prices = prices
        self.last_update = datetime.datetime.now() + datetime.timedelta(days=-1)
        go_on = True
        while go_on:
            go_on = self.main_menu()

    def menu(self, items, inp=''):
        x = PrettyTable(["Key", "Item"])
        x.align["Item"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in items:
            x.add_row(i)
        print(x)
        if inp == '':
            try:
                inp = input().lower()
            except KeyboardInterrupt:
                inp = 'q'
        key = inp[:1]
        inp = inp[1:]
        return key, inp
    def get_historic_quotes(self):
        now = datetime.datetime.now()
#         print(now, self.last_update)
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
#                 print(quote)
                for key in quote:
                    self.prices.update(sec.yahoo_id, key, quote[key]['Close'])
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
#         pdb.set_trace()
        for sec in self.secs:
#             print(sec.name, sec.yahoo_id)
            quote = None
#             quote = self.prices.get_quote('goog')
#             print(quote)
            try:
                quote = ystockquote.get_historical_prices(sec.yahoo_id, day_str, day_str)
            except urllib.error.HTTPError:
                print('No quotes found for:', sec.name)
                self.last_update += datetime.timedelta(seconds=-30)
            else:
#                 print(quote)
                self.prices.update(sec.yahoo_id, day_str, quote[day_str]['Close'])
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
    def portfolio_menu(self, inp=''):
        go_on = True
        menu = []
        menu.append(["a", "Add portfolio"])
#         menu.append(["n", "New security"])
#         menu.append(["e", "Edit security"])
#         menu.append(["d", "Delete security"])
#         menu.append(['u', 'Update security prices'])
#         menu.append(['i', 'Initialize quotes for last 10 years'])
        menu.append(["-", '---'])
        menu.append(["q", "Back"])
        key, inp = self.menu(menu, inp)
        if key == 'a':
            self.new_portfolio()
        elif key == 'q':
            go_on = False  
        return go_on      
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
#         plt.axis(dates)
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
            
        
        
    def securities_menu(self, inp=''):
        go_on = True
        menu = []
        menu.append(["l", "List securities"])
        menu.append(["n", "New security"])
        menu.append(["e", "Edit security"])
        menu.append(["d", "Delete security"])
        menu.append(['u', 'Update security prices'])
        menu.append(['i', 'Initialize quotes for last 15 years'])
        menu.append(["g", "New graph"])
        menu.append(["p", "Stock split"])
        menu.append(["-", '---'])
        menu.append(["q", "Back"])
        key, inp = self.menu(menu, inp)
        if key == 'n':
            self.new_stock()
        elif key == 'e':
            self.edit_stock()
        elif key == 'd':
            self.delete_stock()
        elif key == 'l':
            self.list_stocks()
        elif key == 'i':
            self.get_historic_quotes()
            pprint(self.prices.numbers)
        elif key == 'u':
            self.update_stocks()
            pprint(self.prices.numbers)
        elif key == 'g':
            self.new_graph()
        elif key == 'p':
            self.new_split()
        elif key == 'q':
            go_on = False  
        return go_on      
    def main_menu(self):
        go_on = True
        menu = []
        menu.append(["s", "Securities"])
        menu.append(["p", "Portfolios"])
        menu.append(["t", "New transaction"])
        menu.append(['s', 'Settings (eg. planned savings)'])
        menu.append(['f', 'Forecast'])
        menu.append(["-", '---'])
        menu.append(["q", "Quit"])
        key, inp = self.menu(menu)
        if key == 's':
            self.securities_menu(inp)
        elif key == 'p':
            self.portfolio_menu(inp)
        elif key == 'l':
            self.list_stocks()
        elif key == 'u':
            self.update_stocks()
            pprint(self.prices.numbers)
        elif key == 'q':
            go_on = False  
        return go_on      
    
if __name__ == "__main__":
    DATA = Database()
    try:
        PORTFOLIO = pickle.load(open('portfolio.p', 'rb'))
    except:
        PORTFOLIO = Portfolio('All')
#     print(str(PORTFOLIO).strip('\n'))
    PRICES = Prices(DATA)

    SECS = Securities(DATA, PRICES)
#     print('PRICES')
#     print(PRICES)
    print('SECS')
    print(SECS)
    UI = UI(SECS, PORTFOLIO, PRICES)
    pickle.dump( PORTFOLIO, open('portfolio.p', 'wb'))
#     print('PRICES')
#     print(PRICES)
    print('SECS')
    print(SECS)
    DATA.close()
