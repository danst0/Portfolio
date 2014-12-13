#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
from dateutil import relativedelta

class Helper:
    def rand_str(self):
        num = random.randint(0, 9999)
        return str(num).zfill(4)


    def nice_number(number):
        if number:
            # number = str(round(number, 2))
            # 		if number.find('.') > len(number) - 3:
            # 		    number += '0'
            number = '{:10,.2f}'.format(number)
        return number


class Tools:
    def adjust_dates(self, update_interval, to_date, from_date=None):
        # print(from_date, to_date, to_date.weekday())
        # print(update_interval)
        # import pdb;pdb.set_trace()
        if update_interval == 'quarterly':
            month_delta = to_date.month % 3
            # we do have a quarter month and we are already on the last day
            if month_delta == 0 and to_date == to_date + relativedelta.relativedelta(day=31):
                new_to_date = to_date
            elif month_delta == 0:
                new_to_date = to_date + relativedelta.relativedelta(months=-3)
                new_to_date += relativedelta.relativedelta(day=31)
            # in any month: go back three month, go forward number of mod month
            else:
                new_to_date = to_date + relativedelta.relativedelta(months=-month_delta)
                new_to_date += relativedelta.relativedelta(day=31)

        elif update_interval == 'monthly':
            new_to_date = to_date + relativedelta.relativedelta(days=+1, months=-1)
            new_to_date += relativedelta.relativedelta(day=31)

        elif update_interval == 'weekly':
            new_to_date = to_date + relativedelta.relativedelta(weekday=relativedelta.SU(-1))
        elif update_interval == 'instant':
            new_to_date = to_date
        if from_date:
            delta = (to_date - from_date).days
            # print('delta', delta)
            if delta != 0:
                from_date = new_to_date + relativedelta.relativedelta(days=-delta)
            else:
                from_date = new_to_date + relativedelta.relativedelta(years=-1)
            # print(from_date, to_date, to_date.weekday())
            return new_to_date, from_date
        else:
            return new_to_date

