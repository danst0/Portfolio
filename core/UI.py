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

