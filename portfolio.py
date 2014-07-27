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

class Analyses:
    """Perform additional analyses on the Portfolios and stocks."""
    pass
    
class Database:
    def __init__(self):
#         sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
#         sqlite3.register_adapter(uuid.UUID, lambda u: bytes(u.bytes_le))
        conn = sqlite3.connect('test.db', detect_types=sqlite3.PARSE_DECLTYPES)

        self.conn = sqlite3.connect('data.sql', detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        # Create tables    
        try:
            self.c.execute('''CREATE TABLE transactions (id BLOB PRIMARY KEY, type TEXT, portfolio TEXT, yahoo_id TEXT, date TEXT, nominal REAL, price REAL, cost REAL, total REAL)''')
        except:
            pass
        else:
            print('Created table for transactions')
        try:
            self.c.execute('''CREATE TABLE stocks (id BLOB PRIMARY KEY, name TEXT, yahoo_id TEXT, type TEXT)''')
        except:
            pass
        else:
            print('Created table for stocks')
        try:
            self.c.execute('''CREATE TABLE prices (id BLOB PRIMARY KEY, stock_id BLOB, date TEXT, price REAL)''')
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
        self.data.c.execute('INSERT INTO stocks(id, name, yahoo_id, type) VALUES (?, ?, ?, ?)', (uuid.uuid4().bytes, name, yahoo_id, type))

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
                        if total != total_value + var_charge + fixed_charge:
                            print('Error while importing, totals do not match')
                            sys.exit()
#                         print(line)
#             if print_all:
#                 print(line.replace('.', ''))
            line_counter += 1 
        if not valid:
            return None
        elif type == 'dividende':
            return {'type': 'd', 'name': name, 'date': date, 'value': value}
        elif type == 'kauf':
            return {'type': 'b', 'name': name, 'date': date, 'nominale': nominale, 'value': value, 'cost': fixed_charge + var_charge}  
    def add(self, type, yahoo_id, date, nominal, price, cost, portfolio):
        if yahoo_id != None:
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
                
            self.data.c.execute('INSERT INTO transactions (id, type, portfolio, yahoo_id, date, nominal, price, cost, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (uuid.uuid4().bytes, type, portfolio, yahoo_id, date, nominal, price, cost, total))
            return True
        else:
            return False
#         self.data.commit()
    def get_total_invest(self, portfolio):
        return self.get_total(portfolio, 'b')
    def get_total_divest(self, portfolio):
        return self.get_total(portfolio, 's')
    def get_total_dividend(self, portfolio):
        return self.get_total(portfolio, 'd')
    def get_total(self, portfolio, type):
        result = self.data.c.execute('''SELECT SUM(total) FROM transactions WHERE portfolio = ? AND type = ?''', (portfolio, type)).fetchall()
        return result

    def get_total_for_portfolio(self, portfolio):
        result = self.data.c.execute('''SELECT yahoo_id, SUM(nominal), SUM(cost), SUM(total) FROM transactions WHERE portfolio = ? GROUP BY yahoo_id''', (portfolio,)).fetchall()
        return result

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
    def get_stock_id_from_yahoo_id(self, yahoo_id):
#         print(':'+yahoo_id+':')
        stock_id = self.data.c.execute('''SELECT id FROM stocks WHERE yahoo_id = ?''', (yahoo_id,)).fetchone()
#         print(stock_id)
        return None if stock_id is None else stock_id[0]
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
            self.data.c.execute('''INSERT INTO prices(id, stock_id, date, price) VALUES (?, ?, ?, ?)''', (uuid.uuid4().bytes, id, date, price))
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
    def __init__(self, securities, portfolio, prices, transaction):
        self.secs = securities
        self.portfolio = portfolio
        self.prices = prices
        self.transaction = transaction
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
            try:
                quote = ystockquote.get_historical_prices(sec.yahoo_id, yesterday_str, day_str)
            except urllib.error.HTTPError:
                print('No quotes found for:', sec.name)
                self.last_update += datetime.timedelta(seconds=-30)
            else:
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
    def portfolio_menu(self, inp=''):
        go_on = inp
        menu = []
        menu.append(["a", "Add portfolio"])
        menu.append(["l", "List portfolios"])
        menu.append(["c", "List content of portfolio"])
        menu.append(["-", '---'])
        menu.append(["q", "Back"])
        key, inp = self.menu(menu, inp)
        if key == 'a':
            self.new_portfolio()
        elif key == 'l':
            print(self.portfolio)
        elif key == 'c':
            print(self.portfolio)
            self.list_content()
        elif key == 'q':
            go_on = inp
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
            
    def settings_menu(self):
        go_on = inp
        menu = []
        menu.append(["a", 'Planned saving (p.m.)'])
        menu.append(["b", ''])
        menu.append(["c", ''])
        menu.append(["d", ''])
        menu.append(["-", '---'])
        menu.append(["q", "Back"])
        key, inp = self.menu(menu, inp)
        if key == 'a':
            self.new_stock()
        elif key == 'b':
            self.edit_stock()
        elif key == 'q':
            go_on = inp
        return go_on      
    def main_menu(self):
        go_on = ''
        menu = []
        menu.append(["s", "Securities"])
        menu.append(["p", "Portfolios"])
        menu.append(["t", "New transaction"])
        menu.append(["i", "Import from PDFs"])
        menu.append(['e', 'Settings (eg. planned savings)'])
        menu.append(['f', 'Forecast'])
        menu.append(["-", '---'])
        menu.append(["q", "Quit"])
        while True:
            key, inp = self.menu(menu, go_on)
            if key == 's':
                inp = self.securities_menu(inp)
            elif key == 'p':
                inp = self.portfolio_menu(inp)
            elif key == 'e':
                inp = self.settings_menu()
            elif key == 't':
                self.new_transaction()
            elif key == 'i':
                self.import_pdfs()
            elif key == 'q':
                go_on = ''
                break
    def import_pdfs(self):
        base_path = '/Users/danst/Desktop/PDFs'
        for file in os.listdir(base_path):
            if file.endswith('.pdf'):
                print('Import ' + file)
                data = self.transaction.get_data_from_text(subprocess.check_output(['/usr/local/bin/pdf2txt.py', base_path + '/' + file]).decode("utf-8"))
                if data != None:
#                     print(data)
                    if data['type'] in ['b', 's']:
                        if not self.transaction.add(data['type'], self.secs.find_stock(data['name']), data['date'], data['nominale'], data['value'], data['cost'], 'All'):
                            print(data['name'] +': could not add transaction (e.g. security not available)')
                        else:
                            print('Transaction successful')
                    elif data['type'] in ['d']:
                        if not self.transaction.add(data['type'], self.secs.find_stock(data['name']), data['date'], 0, data['value'], 0, 'All'):
                            print(data['name'] +': could not add transaction (e.g. security not available)')
                        else:
                            print('Transaction successful')
                    
                
#                 break
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
        self.transaction.add(type, self.secs.find_stock(stock), date, nom, price, cost, portfolio)
    
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
    TRANSACTION = Transaction(DATA)
    UI = UI(SECS, PORTFOLIO, PRICES, TRANSACTION)
    pickle.dump( PORTFOLIO, open('portfolio.p', 'wb'))
#     print('PRICES')
#     print(PRICES)
    print('SECS')
    print(SECS)
    DATA.close()
