#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import datetime
import uuid

from prettytable import PrettyTable


class Transaction:
    """Class to store transactions"""



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
            result = self.data.c.execute(
                '''SELECT id FROM transactions WHERE type = ? AND portfolio = ? AND stock_id = ? AND date = ? AND nominal = ? AND price = ? AND cost = ? AND total = ?''',
                (type, portfolio, stock_id, date, nominal, price, cost, total)).fetchall()

            if result == []:
                self.data.c.execute(
                    'INSERT INTO transactions (id, type, portfolio, stock_id, date, nominal, price, cost, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (uuid.uuid4(), type, portfolio, stock_id, date, nominal, price, cost, total))
                self.money.update('settlement', date, total)
                if type != 'd' and price != 0.0:
                    self.prices.update(self.secs.get_isin_id_from_stock_id(stock_id), date, price)
                print('Cash addition ' + str(total))
                return True
            else:
                print('Transaction already seems to exist: ' + str(result))
                return False
        else:
            return False

    # self.data.commit()
    def get_invest_divest(self, portfolio, stock_id, from_date, to_date):
        in_divest = self.get_total(portfolio, 'b', from_date, to_date, stock_id)
        in_divest += self.get_total(portfolio, 's', from_date, to_date, stock_id)
        return in_divest

    def get_total_invest(self, portfolio, from_date, to_date):
        return self.get_total(portfolio, 'b', from_date, to_date)

    def get_total_divest(self, portfolio, from_date, to_date):
        return self.get_total(portfolio, 's', from_date, to_date)

    def get_total_dividend(self, portfolio, from_date, to_date):
        return self.get_total(portfolio, 'd', from_date, to_date)

    def get_total(self, portfolio, type, from_date, to_date, stock_id=None):
        if stock_id:
            result = self.data.c.execute(
                '''SELECT SUM(total) FROM transactions WHERE portfolio = ? AND type = ? AND date > ? AND date <= ? AND stock_id = ?''',
                (portfolio, type, from_date, to_date, stock_id)).fetchall()
        else:
            result = self.data.c.execute(
                '''SELECT SUM(total) FROM transactions WHERE portfolio = ? AND type = ? AND date > ? AND date <= ?''',
                (portfolio, type, from_date, to_date)).fetchall()

            # print('get_total ', result)
        if result != None:
            result = result[0]
            if result != None:
                result = result[0]
        if result == None:
            result = 0.0
        return result



    def get_total_for_portfolio(self, portfolio):
        result = self.data.c.execute(
            '''SELECT name, SUM(nominal), SUM(cost), SUM(total) FROM transactions INNER JOIN stocks ON stocks.id = transactions.stock_id WHERE portfolio = ? GROUP BY stock_id''',
            (portfolio,)).fetchall()
        # for item in result
        return result

    def __repr__(self):
        keys = ['Name', 'Type', 'Date', 'Total']
        result = self.data.c.execute(
            '''SELECT stock_id, type, date, total FROM transactions ORDER BY date DESC''').fetchall()
        x = PrettyTable(keys)
        x.padding_width = 1  # One space between column edges and contents (default)
        for item in result:
            item = list(item)
            item[0] = self.secs.get_name_from_stock_id(item[0])
            x.add_row(item)
        return str(x)