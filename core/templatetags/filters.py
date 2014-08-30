from django import template


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
            result = str(round(number, 2))
        except TypeError:
            result = number
    else:
        result = ''
    return result
