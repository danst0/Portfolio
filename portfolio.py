#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import sqlite3
import uuid
import subprocess


import matplotlib.pyplot as plt
# Sample stocks        
# +--------------------+---------+-------+------------+
# | Name               |    ID   |  Type | Last price |
# +--------------------+---------+-------+------------+
# | Aareal Bank AG     |  ARL.DE | Stock |   32.25    |
# | Apple Inc.         |  APC.F  | Stock |    72.5    |
# | Host Marriot       |  HMT.F  |  REIT |   16.72    |
# | DB TR EU Renten 1C | DBXN.DE |  Bond |   209.37   |
# | DB MSCI EU M 1C    | DX2I.DE | Stock |    73.7    |
# +--------------------+---------+-------+------------+

# Next todo: get price from specific date, multiply by number of stocks



class Analyses:
    """Perform additional analyses on the Portfolios and stocks."""
    pass
    
class Database:
    def __init__(self):
        sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes=b))
        sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes)

        self.conn = sqlite3.connect('data.sql', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        # Create tables    
        try:
            self.c.execute('''CREATE TABLE transactions (id GUID PRIMARY KEY, type TEXT, portfolio TEXT, stock_id GUID, date TEXT, nominal REAL, price REAL, cost REAL, total REAL)''')
        except:
            pass
        else:
            print('Created table for transactions')
        try:
            self.c.execute('''CREATE TABLE stocks (id GUID PRIMARY KEY, name TEXT, yahoo_id TEXT, type TEXT)''')
        except:
            pass
        else:
            print('Created table for stocks')
        try:
            self.c.execute('''CREATE TABLE prices (id GUID PRIMARY KEY, stock_id GUID, date TEXT, price REAL)''')
        except:
            pass
        else:
            print('Created table for prices')
    def commit(self):
        self.conn.commit()
    def close(self):
        self.conn.commit()
        self.conn.close()
        
class Portfolio:
    """Collection of different portfolios or stocks."""
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name
        self.children = []
        self.child_securities = []
        self.cash = 0.0
    def add_security(self, parent, stock_id):
        if self.name == parent:
            self.child_securities.append(stock_id)
        else:
            for i in self.children:
                i.add_security(parent, stock_id)
    def add_portfolio(self, parent, name):
        if self.name == parent:
            self.children.append(Portfolio(name, parent))
        else:
            for i in self.children:
                i.add_portfolio(parent, name)
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
        self.keys = ['Name', 'ID', 'Type']
    def list(self):
        return (self.name, self.yahoo_id, self.type)
    def __str__(self):
        x = PrettyTable(self.keys)
        x.align[self.keys[0]] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        x.add_row(self.list())
        return str(x)

class Securities:
    """Wrapper for all stored securities"""
    keys = ['Name', 'ID', 'Type', 'Last price']
    def __init__(self, data):
        self.data = data
        self.securities = []
        all = self.data.c.execute('SELECT * FROM stocks')
        for line in all.fetchall():

            self.securities.append(Security(*line[1:]))
#         print(self.securities)
        self.prices = None

    def add(self, name, yahoo_id, type):
        self.securities.append(Security(name, yahoo_id, type))
        self.data.c.execute('INSERT INTO stocks(id, name, yahoo_id, type) VALUES (?, ?, ?, ?)', (uuid.uuid4(), name, yahoo_id, type))
    def change_stock(self, yahoo_id, sec):
        found = False
        for num, item in enumerate(self.securities):
            if yahoo_id.lower() in item.yahoo_id.lower():
                found = True
                self.securities[num] = sec
                self.data.c.execute('UPDATE stocks set name = ?, yahoo_id = ?, type = ? WHERE yahoo_id = ?', (sec.name, sec.yahoo_id, sec.type, yahoo_id))
                break
        return found
    def delete_stock(self, yahoo_id):
        found = False
        for num, item in enumerate(self.securities):
            if yahoo_id.lower() in item.yahoo_id.lower():
                found = True
                self.securities.pop(num)
                self.data.c.execute('DELETE FROM stocks WHERE yahoo_id = ?', (yahoo_id,))
                break
        return found      
#         pickle.dump( self.securities, open( "securities.p", "wb" ) )
    def empty(self):
        return False if len(self.securities) > 0 else True
    def get_name_from_stock_id(self, stock_id):
        name = self.data.c.execute('''SELECT name FROM stocks WHERE id = ?''', (stock_id,)).fetchone()
        return None if name is None else name[0]

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
    def find_stock(self, stock_id_or_name, return_obj=False):
        found = None
        found_obj = None
        for item  in self.securities:
            if (stock_id_or_name.lower() in item.name.lower() or
                stock_id_or_name.lower() in item.yahoo_id.lower()):
                found = item.yahoo_id
                found_obj = item
                break
        if return_obj:
            return found_obj
        else:
            return found
    def get_stock_id_from_yahoo_id(self, yahoo_id):
        stock_id = self.data.c.execute('''SELECT id FROM stocks WHERE yahoo_id = ?''', (yahoo_id,)).fetchone()
        return None if stock_id is None else stock_id[0]

class Transaction:
    """Class to store transactions"""
    def __init__(self, data):
        self.data = data
    def get_data_from_text(self, text):
        valid = False
        type = ''
        line_counter = 0
        lines = text.split('\n')
        print_all = False
        total_value = None
        while line_counter < len(lines):
            line = lines[line_counter]
            if line.find('Daniel Dumke') != -1:
                valid = True
#                 print('Valid document for Daniel Dumke')
            if valid:
                if type == '':
                    if line.find('DIVIDENDENGUTSCHRIFT ') != -1:
                        type = 'dividende'
                    elif line.find('ERTRAGSGUTSCHRIFT') != -1:
                        type = 'dividende'
                    elif line.find('WERTPAPIERABRECHNUNG') != -1:
#                         print_all = True
                        line_counter += 1 
                        line = lines[line_counter]
                        if line.find('KAUF') != -1:
                            type = 'kauf'
                        elif line.find('VERKAUF') != -1:
                            type = 'verkauf'
                else:
                    if line.find('WKN') != -1:
#                         print(line)
                        try:
                            wkn = re.match('.*WKN.*([A-Z0-9]{6}).*', line).group(1)
                        except:
                            pass
                        else:
#                             print(wkn)
                            line_counter += 1 
                            line = lines[line_counter]
                            name = line.strip(' ')
#                             print(name)   
                    elif line.find('WERT') != -1:
#                         print(line)
                        result = re.match('WERT\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4}).*([A-Z]{3})\s*([0-9\.,]*)', line)
                        date = datetime.datetime.strptime(result.group(1), "%d.%m.%Y").date()
                        currency = result.group(2)
                        if currency != 'EUR':
                            print('Error while importing, currency not EUR')
                            sys.exit()
                        value = float(result.group(3).replace('.','').replace(',','.'))
#                         print(date, currency, value)                   
#                         print(result)

                    elif line.find('Umsatz') != -1:
                    # Nominale when buying
#                         print(line)
                        line_counter += 1 
                        line = lines[line_counter]
#                         print(line)
                        nominale = float(line.replace(',','.'))
#                         print(nominale)
                    elif line == 'Wertpapier':
                    # Nominale when buying
#                         print(line)
                        line_counter += 1 
                        line = lines[line_counter]
                        name = line.strip(' ')
#                         print(name)
                    
                    elif re.match('AM.*([0-9\.]{10}).*UM.*', line) != None:
                        date = re.match('AM.*([0-9\.]{10}).*UM.*', line).group(1)
                        date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
#                         print(date)
                    elif line == 'Kurs':
                    # Nominale when buying
#                         print(line)
                        line_counter += 2
                        line = lines[line_counter]
#                         print(line)                                       
                        value = float(line.split(' ')[0].replace(',','.'))
#                         print(value)
                        total_value = value * nominale
#                         print(total_value)
#                         print('total value ', total_value)
#                         print_all = True
                    elif line.replace('.', '').find(str(total_value).replace('.',',')) != -1:
                    # Nominale when buying
#                         print(line)
                        line_counter += 1 
                        line = lines[line_counter]
                        var_charge = float(line.replace('.', '').replace(',', '.'))
#                         print(var_charge)
                        line_counter += 1 
                        line = lines[line_counter]
                        fixed_charge = float(line.replace('.', '').replace(',', '.'))
#                         print(fixed_charge)
                        line_counter += 1 
                        line = lines[line_counter]
                        total = float(line.replace('.', '').replace(',', '.'))
#                         print(total)
#                         print(total_value + var_charge + fixed_charge, total)
#                         print(abs(total - (total_value + var_charge + fixed_charge)))
                        if abs(total - (total_value + var_charge + fixed_charge)) > 0.01:
                            print('Error while importing, totals do not match')
                            sys.exit()
#                         print(line)
#             if print_all:
#             print(line.replace('.', ''))
            line_counter += 1 
        if not valid:
            return None
        elif type == 'dividende':
            return {'type': 'd', 'name': name, 'date': date, 'value': value}
        elif type == 'kauf':
            return {'type': 'b', 'name': name, 'date': date, 'nominale': nominale, 'value': value, 'cost': fixed_charge + var_charge}  
    def add(self, type, stock_id, date, nominal, price, cost, portfolio):
        if stock_id != None:
            if price < 0:
                price = -1 * price
            if cost < 0:
                cost = -1 * cost
            if type == 'b':
                if nominal < 0:
                    nominal = -1 * nominal
                total = -1 * price * nominal - cost
            elif type == 's':
                if nominal > 0:
                    nominal = -1 * nominal
                total = -1 * price * nominal + cost
            elif type == 'd':
                if nominal != 0:
                    price = price * nominal
                    nominal = 0
                cost = 0
                total = price
            result = self.data.c.execute('''SELECT id FROM transactions WHERE type = ? AND portfolio = ? AND stock_id = ? AND date = ? AND nominal = ? AND price = ? AND cost = ? AND total = ?''', (type, portfolio, stock_id, date, nominal, price, cost, total)).fetchall()

            if result == []:
                self.data.c.execute('INSERT INTO transactions (id, type, portfolio, stock_id, date, nominal, price, cost, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (uuid.uuid4(), type, portfolio, stock_id, date, nominal, price, cost, total))
                return True
            else:
                print('Transaction already seems to exist!')
                return False
        else:
            return False
#         self.data.commit()
    def get_total_invest(self, portfolio, from_date, to_date):
        return self.get_total(portfolio, 'b', from_date, to_date)
    def get_total_divest(self, portfolio, from_date, to_date):
        return self.get_total(portfolio, 's', from_date, to_date)
    def get_total_dividend(self, portfolio, from_date, to_date):
        return self.get_total(portfolio, 'd', from_date, to_date)
    def get_total(self, portfolio, type, from_date, to_date):
        result = self.data.c.execute('''SELECT SUM(total) FROM transactions WHERE portfolio = ? AND type = ? AND date >= ? AND date <= ?''', (portfolio, type, from_date, to_date)).fetchall()
        if result != None:
            result = result[0]
            if result != None:
                result = result[0]
        if result == None:
            result = 0.0
        return result
    def get_portfolio(self, portfolio, date):
        """Get portfolio contents on that specific date, incl. all transactions from that date"""
        result = self.data.c.execute("""SELECT stock_id, nominal FROM transactions WHERE portfolio = ? AND (type = 'b' OR type = 's') AND date <= ?""", (portfolio, date)).fetchall()
        stocks = {}
        for item in result:
            if item[0] not in stocks.keys():
                stocks[item[0]] = 0.0
            stocks[item[0]] = stocks[item[0]] + item[1]
        return stocks

    def get_total_for_portfolio(self, portfolio):
        result = self.data.c.execute('''SELECT yahoo_id, SUM(nominal), SUM(cost), SUM(total) FROM transactions WHERE portfolio = ? GROUP BY yahoo_id''', (portfolio,)).fetchall()
        return result
    def __repr__(self):
        keys = ['ID', 'Type', 'Date', 'Total']
        result = self.data.c.execute('''SELECT stock_id, type, date, total FROM transactions''').fetchall()
        x = PrettyTable(keys)
        x.padding_width = 1 # One space between column edges and contents (default)
        for item in result:
            x.add_row(item)
        return str(x)
        
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
    def delete_prices(self, yahoo_id):
        stock_id = self.get_stock_id_from_yahoo_id(yahoo_id)
        self.data.c.execute('''DELETE FROM prices WHERE stock_id = ?''', (stock_id, ))
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

    def row_exists(self, stock_id, date):
        result = self.data.c.execute('''SELECT price FROM prices WHERE stock_id = ? AND date = ?''', (stock_id, date)).fetchone()
        return False if result == None else True
    def update(self, yahoo_id, date, price):
        id = self.secs.get_stock_id_from_yahoo_id(yahoo_id)
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
    def get_prices(self, id):
        id = self.secs.get_stock_id_from_yahoo_id(id)
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
    def get_quote(self, symbol):
        print(symbol)
        base_url = 'http://www.boerse-frankfurt.de/en/search/result?order_by=wm_vbfw.name&name_isin_wkn='
        content = urllib.request.urlopen(base_url + symbol).read().decode('UTF-8')#.replace('\n','')

        quote = None
        if content.find('Disclaimer nicht akzeptiert: kaufen') != -1:
            m = re.search('Last Price.{1,100}<span.{1,45}security-price.{1,55}>([0-9\.]{3,9})<\/', content, re.DOTALL)
            if m:
                quote = float(m.group(1))
        else:
            print('Policy has to be accepted first')
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
    def list_content(self):

        pf = input('Portfolio [All] ')
        if pf == '':
            pf = 'All'
        transactions = self.transaction.get_total_for_portfolio(pf)
#         print(transactions)
        
        x = PrettyTable(['ID', 'Nominal', 'Cost', 'Value'])
        x.align['Invested'] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
#         print(transactions)
        for i in transactions:
#             print(i)
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
        go_on = inp
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
            print('Start update')
            self.get_historic_quotes()
            print('Update finished')
        elif key == 'u':
            print('Start update')
            self.update_stocks()
            print('Update finished')
        elif key == 'g':
            self.new_graph()
        elif key == 'p':
            self.new_split()
        elif key == 'q':
            go_on = inp
        return go_on
    def edit_stock(self):
        stock = input('Name of security ')
        stock_obj = self.secs.find_stock(stock, return_obj=True)
        print(stock_obj)
        new_name = input('New name (empty for no change) ')
        if new_name == '':
            new_name = stock_obj.name
        new_id = input('New id (empty for no change) ')
        if new_id== '':
            new_id = stock_obj.yahoo_id
        new_type = input('New Type (empty for no change) ')
        if new_type == '':
            new_type = stock_obj.type
        self.secs.change_stock(stock_obj.yahoo_id, Security(new_name, new_id, new_type))
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
#         print(stocks)
        keys = ['Name', 'Nominal', 'Price', 'Value']        
        x = PrettyTable(keys)
        x.padding_width = 1 # One space between column edges and contents (default)
        prices = []
        tmp = 0.0
        for key in stocks.keys():
            price = self.prices.get_price(key, my_date.strftime("%Y-%m-%d"))
            value = stocks[key] * price
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
    def analyzes_menu(self, inp=''):
        return self.new_menu(
            [   'List portfolio',
                'Profitability'],
            [   self.list_portfolio,
                self.profitability], inp)
    def settings_menu(self, inp=''):
        return self.new_menu(
            [   'Planned saving (p.m.)'],
            [   None], inp)
    def portfolio_menu(self, inp=''):
        return self.new_menu(
            [   'Add portfolio',
                'List portfolios',
                'List content of portfolio'],
            [   self.new_portfolio,
                self.print_portfolio,
                self.list_portfolio_contents], inp)
    def main_menu(self):
        self.new_menu(
            [   'Analyzes - Menu',
                'Securities - Menu',
                'Portfolios - Menu',
                'New transaction',
                'Import from PDFs',
                'Settings (eg. planned savings)',
                'Forecast'],
            [   self.analyzes_menu,
                self.securities_menu,
                self.portfolio_menu,
                self.settings_menu,
                self.new_transaction,
                self.import_pdfs,
                None])
    def new_menu(self, choices, functions, inp=''):
        letters = 'abcdefghijklmnoprstuvwxyz'
        while True:
            x = PrettyTable(["Key", "Item"])
            x.align["Item"] = "l"
            x.padding_width = 1 # One space between column edges and contents (default)
            for num, choice in enumerate(choices):
                x.add_row([letters[num], choice])
#                 i[1] = i[1].replace(' - Menu', '')
            x.add_row(["-", '---'])
            x.add_row(["q", "Quit"])
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
        base_path = '/Users/danst/Desktop/PDFs'
        for file in os.listdir(base_path):
            if file.endswith('.pdf'):
                print('Import ' + file)
                data = self.transaction.get_data_from_text(subprocess.check_output(['/usr/local/bin/pdf2txt.py', base_path + '/' + file]).decode("utf-8"))
                if data != None:
#                     print(data)
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
#     print('PRICES')
#     print(PRICES)
    print('SECS')
    print(SECS)
    TRANSACTION = Transaction(DATA)
    UI = UI(SECS, PORTFOLIO, PRICES, TRANSACTION)
    pickle.dump( PORTFOLIO, open('portfolio.p', 'wb'))
#     print('PRICES')
#     print(PRICES)
    print('SECS')
    print(SECS)
    print('TRANSACTIONS')
    print(TRANSACTION)
    DATA.close()
