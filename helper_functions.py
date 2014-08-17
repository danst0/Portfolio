#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random

def rand_str():
	num = random.randint(0,9999)
	return str(num).zfill(4)
def nice_number(number):
	if number:
# 		number = str(round(number, 2))
# 		if number.find('.') > len(number) - 3:
# 		    number += '0'
		number = '{:20,.2f}'.format(number)
	return number