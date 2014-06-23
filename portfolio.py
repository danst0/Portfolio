#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prettytable import PrettyTable

class Analyses:
    """Perform additional analyses on the Portfolios and stocks."""
    pass
    
class Portfolio:
    """Collection of different portfolios or stocks."""
    pass

class Security:
    """Class for stocks, bond, cash, everything is a security."""
    def __init__(self, name, id, type):
        self.name = name
        self.id = id
        self.type = type

class Securities:
    """Wrapper for all stored securities"""
    securities = []
    keys = ['Name', 'ID', 'Type']
    def add(self, *args):
        securities.append(Security(*args))
    def __str__(self):
        x = PrettyTable(self.keys)
        x.align[self.keys[0]] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in self.securities:
            x.add_row(i)
        return x
        
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
    def __init__(self, securities):
        self.secs = securities
        while True:
            self.main_menu()
            try:
                key = input().lower()
            except KeyboardInterrupt:
                key = 'q'
            if key == "s":
                self.new_stock()
            elif key == 'q':
                break
    def menu(self, items):
        x = PrettyTable(["Key", "Item"])
        x.align["Item"] = "l" # Left align city names
        x.padding_width = 1 # One space between column edges and contents (default)
        for i in items:
            x.add_row(i)
        print(x)
                
    def new_stock(self):
        print "Name ", 
        name = input()
        print "ID ",
        id = input()
        print "Type ",
        type = input()
        self.secs.add(name, id, type)
        
    def main_menu(self):
        menu = []
        menu.append(["s", "New stock"])
        menu.append(["p", "New portfolio"])
        menu.append(["t", "New transaction"])
        menu.append(["l", "List stocks in portfolio"])
        menu.append(["-", '---'])
        menu.append(["q", "Quit"])
        self.menu(menu)
    
if __name__ == "__main__":
    SECS = Securities()
    UI = UI(SECS)
    print(SECS)
    
