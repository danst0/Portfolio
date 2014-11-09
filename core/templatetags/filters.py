from django import template
# import locale
import math
from decimal import Decimal

register = template.Library()

@register.filter
def keyvalue(dict, key):
    try:
        return dict[key]
    except KeyError:
        return ''

@register.filter
def nicenumber(number):
    if number and number != 0:
        try:
            # locale.setlocale(locale.LC_NUMERIC, 'german')
            result = '{:10,.0f}'.format(number)
            # result = str(round(number, 2))
        except TypeError:
            result = number
        except ValueError:
            result = number
    else:
        result = ''
    return result

@register.filter
def nicenumber_100(number):
    if number and number != 0:
        try:
            result = nicenumber(int(number/100)*100)
        except TypeError:
            result = number
    else:
        result = ''
    return result

@register.filter
def cut(number, digits):
    multiplier = Decimal(max(math.pow(10, digits), 1))
    rounding_factor = multiplier/Decimal(2)
    result = int((number+rounding_factor)/multiplier)*multiplier
    return result

@register.filter
def absolute(number):
    number = abs(number)
    return number