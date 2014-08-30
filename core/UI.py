#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import os
import subprocess
import sys
import codecs

from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable



from Securities import Security
from input_methods import *
from helper_functions import *


class UI:
    """Class to display user interface."""

    def __init__(self, securities, portfolio, prices, transaction, money):
        self.secs = securities
        self.portfolio = portfolio
        self.prices = prices
        self.transaction = transaction
        self.money = money
        self.last_update = datetime.datetime.now() + datetime.timedelta(days=-1)
        go_on = True
        while go_on:
            go_on = self.main_menu()
        random.seed()



    def update_stocks(self):
        print('Start update')
        now = datetime.datetime.now()
        if now < self.last_update + datetime.timedelta(seconds=30):
            print('Please leave at least 30 secs between each update.')
            return
        else:
            self.last_update = now
        today = datetime.date.today()
        if today.weekday() >= 5:
            today = today + datetime.timedelta(days=4 - today.weekday())
        yesterday = today + datetime.timedelta(days=-1)
        day_str = today.strftime('%Y-%m-%d')
        yesterday_str = yesterday.strftime('%Y-%m-%d')
        for sec in self.secs:
            if not sec.isin_id.startswith('unknown'):
                quote = None
                quote = self.prices.get_quote(sec.isin_id)
                if not quote:
                    print('No quotes found for:', sec.name)
                    self.last_update += datetime.timedelta(seconds=-30)
                else:
                    self.prices.update(sec.isin_id, day_str, quote)
            else:
                print('No ISIN for', sec.name)
        print('Update finished')

    def list_stocks(self):
        if not self.secs.empty():
            print(self.secs)
        else:
            print('No stocks in database.')

    def new_stock(self):
        print('Name ', )
        name = input()
        print('Aliases (comma separated) ', )
        aliases = input().split(',')
        # print(aliases)
        for num in range(len(aliases)):
            aliases[num] = aliases[num].strip()
        rand_id = 'n/a' + rand_str()
        isin_id = input_string('ISIN', '[A-Z]{2}[0-9]{10}', rand_id)
        yahoo_id = input_string('Yahoo ID', '[A-Z0-9]{1,10}', rand_id)
        type = input_string('Type', 'Stock|Bond|REIT')
        self.secs.add(name, aliases, isin_id, yahoo_id, type)

    def list_content(self):

        pf = input('Portfolio [All] ')
        if pf == '':
            pf = 'All'
        transactions = self.transaction.get_total_for_portfolio(pf)
        # print(transactions)

        x = PrettyTable(['Name', 'Nominal', 'Cost', 'Value'])
        x.align['Invested'] = "l"  # Left align city names
        x.padding_width = 1  # One space between column edges and contents (default)
        #		  print(transactions)
        for i in sorted(transactions, key=lambda x: x[0].lower()):
            #			  print(i)
            x.add_row(i[:-1] + (self.prices.get_last_price(i[0], none_equals_zero=True) * i[1],))
        print(x)


    def new_portfolio(self):
        print(self.portfolio)
        print('Parent ', )
        parent = input()

        print('Name ', )
        name = input()

        self.portfolio.add(parent, name)

    def new_graph(self):
        print('Security', )
        stock = input()
        tmp_default = (datetime.date.today() - datetime.timedelta(days=12 * 30)).strftime('%Y-%m-%d')
        print('Start date [' + tmp_default + ']', )
        from_date = input()
        if from_date == '':
            from_date = tmp_default
        from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
        tmp_default = datetime.date.today().strftime('%Y-%m-%d')
        print('End date [' + tmp_default + ']', )
        to_date = input()
        if to_date == '':
            to_date = tmp_default
        to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
        dates, values = self.prices.get_dates_and_prices(self.secs.find(stock), from_date, to_date)
        plt.plot(dates, values, 'r')
        # plt.axis(dates)
        plt.ylabel(self.secs.find(stock))
        plt.xlabel('Date')
        plt.show()

    def new_split(self):
        print('Security', )
        stock = input()
        last_unsplit_date, suggested_ratio = self.prices.find_split_date(self.secs.find(stock))
        print('Last unsplit date [' + last_unsplit_date + ']', )
        split_date = input()
        if split_date == '':
            split_date = last_unsplit_date
        print('Split ratio [' + str(suggested_ratio) + '] for one existing stock')
        ratio = input()
        if ratio == '':
            ratio = suggested_ratio
        dates, values = self.prices.get_dates_and_prices(self.secs.find(stock), None, split_date)
        # print(dates)
        #		print('Update all security prices starting ' + last_unsplit_date + ' into all past available; price is divided by ' + str(ratio))
        #		print('Please manually add a corresponding transaction to internalize the value reduction in the stock nominale.')
        go_on = input_yes(
            'Update all security prices starting ' + last_unsplit_date + ' into all past available; price is divided by ' + str(
                ratio))
        if go_on:
            print('Changing prices')
            for i in range(len(dates)):
                self.prices.update(self.secs.find(stock), dates[i], values[i] / float(ratio))
            stocks_at_split = self.transaction.get_portfolio('All', split_date)
            stock_id = self.secs.get_stock_id_from_isin_id(self.secs.find(stock))
            number_before_split = stocks_at_split[stock_id]
            #			print(stocks_at_split)
            #			print(stock_id)
            #		print(number_before_split)
            number_after_split = number_before_split * ratio
            date_after_split = (
            datetime.datetime.strptime(split_date, '%Y-%m-%d') + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            print('Adding additional stocks')
            self.transaction.add('b', stock_id, date_after_split, number_after_split - number_before_split, 0.0, 0.0,
                                 'All')


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
        # print(stocks_at_start)
        print('Portfolio at start date', from_date.strftime("%Y-%m-%d"))
        self.portfolio.list_pf(from_date)
        print('Portfolio at end date', to_date.strftime("%Y-%m-%d"))
        self.portfolio.list_pf(to_date)
        portfolio_value_at_start = 0.0
        for key in stocks_at_start.keys():
            portfolio_value_at_start += stocks_at_start[key] * self.prices.get_last_price_from_stock_id(key,
                                                                                                        from_date.strftime(
                                                                                                            "%Y-%m-%d"),
                                                                                                        none_equals_zero=True)
        stocks_at_end = self.transaction.get_portfolio('All', to_date.strftime("%Y-%m-%d"))
        portfolio_value_at_end = 0.0
        for key in stocks_at_end.keys():
            portfolio_value_at_end += stocks_at_end[key] * self.prices.get_last_price_from_stock_id(key,
                                                                                                    to_date.strftime(
                                                                                                        "%Y-%m-%d"),
                                                                                                    none_equals_zero=True)

        invest = self.transaction.get_total_invest('All', from_date, to_date)
        divest = self.transaction.get_total_divest('All', from_date, to_date)
        dividend = self.transaction.get_total_dividend('All', from_date, to_date)

        profit_incl_on_books = portfolio_value_at_end + invest - divest - portfolio_value_at_start + dividend
        print('Absolute KPIs')
        keys = ['Start portfolio', 'Investment', 'Divestment', 'Current portfolio', 'Dividend',
                'Profit (incl. on books)']
        x = PrettyTable(keys)
        x.padding_width = 1  # One space between column edges and contents (default)
        x.add_row([nice_number(portfolio_value_at_start), nice_number(-invest), nice_number(divest),
                   nice_number(portfolio_value_at_end), nice_number(dividend), nice_number(profit_incl_on_books)])
        print(str(x))
        print('Relative KPIs')
        keys = ['ROI']
        x = PrettyTable(keys)
        x.padding_width = 1  # One space between column edges and contents (default)
        if portfolio_value_at_start - invest != 0:
            tmp = [nice_number(100 * profit_incl_on_books / (portfolio_value_at_start - invest)) + '%']
        else:
            tmp = ['n/a']
        x.add_row(tmp)
        print(str(x))

    def last_day_of_last_month(self, date):
        return date.replace(day=1) - datetime.timedelta(days=1)

    def cash_info(self):
        tmp_default = self.last_day_of_last_month(datetime.date.today()).strftime('%Y-%m-%d')
        my_date = input('Date of state [' + tmp_default + '] ')
        if my_date == '':
            my_date = tmp_default
        my_income = input('Income in month ')
        my_total = input('Total cash at hand (w/o portfolios) ')
        self.money.add_income(my_date, my_income)
        self.money.add_total(my_date, my_total)



    def savings(self):
        tmp_default = self.last_day_of_last_month(datetime.date.today() - relativedelta(months=1)).strftime('%Y-%m-%d')
        from_date = input('From date [' + tmp_default + '] ')
        if from_date == '':
            from_date = tmp_default
        tmp_default = self.last_day_of_last_month(datetime.date.today()).strftime('%Y-%m-%d')
        to_date = input('To date [' + tmp_default + '] ')
        if to_date == '':
            to_date = tmp_default
        self.money.get_all(from_date, to_date)

