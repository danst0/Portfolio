#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
from prettytable import PrettyTable
import sys

class Analyses:
    """Perform additional analyses on the Portfolios and stocks."""
    pass
    
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
    def __init__(self, name, id, type):
        self.name = name
        self.id = id
        self.type = type
    def list(self):
        return (self.name, self.id, self.type)
    def __str__(self):
        return ' '.join(self.list())

class Securities:
    """Wrapper for all stored securities"""
    keys = ['Name', 'ID', 'Type']
    def __init__(self):
        try:
            self.securities = pickle.load( open( "securities.p", "rb" ) )
        except:
            self.securities = []
    def add(self, *args):
        self.securities.append(Security(*args))
        pickle.dump( self.securities, open( "securities.p", "wb" ) )
    def empty(self):
        return False if len(self.securities)>0 else True
    def __str__(self):
        x = PrettyTable(self.keys)
        x.align[self.keys[0]] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in self.securities:
            x.add_row(i.list())
        return str(x)
        
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
    pass
    
class UI:
    """Class to display user interface."""
    def __init__(self, securities, portfolio):
        self.secs = securities
        self.portfolio = portfolio
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
                elif key == 'q':
                    sys.exit()
    def menu(self, items):
        x = PrettyTable(["Key", "Item"])
        x.align["Item"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in items:
            x.add_row(i)
        print(x)
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
        menu.append(["-", '---'])
        menu.append(["q", "Quit"])
        self.menu(menu)
    
if __name__ == "__main__":
    try:
        PORTFOLIO = pickle.load(open('portfolio.p', 'rb'))
    except:
        PORTFOLIO = Portfolio('All')
    print(str(PORTFOLIO).strip('\n'))
    SECS = Securities()
    UI = UI(SECS, PORTFOLIO)
    print(SECS)
    pickle.dump( PORTFOLIO, open('portfolio.p', 'wb'))
    
