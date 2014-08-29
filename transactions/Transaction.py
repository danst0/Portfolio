#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import datetime
import uuid

from prettytable import PrettyTable


class Transaction:
    """Class to store transactions"""



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