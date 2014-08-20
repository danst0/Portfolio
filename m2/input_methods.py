#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
def input_general(text):
    if not text.endswith(' '):
        text += ' '
    try:
        feedback = input(text)
    except:
        feedback = None
    return feedback
def input_float(text):
    while True:
        feedback = input_general(text)
        if feedback == '':
            feedback = '0.0'
        if feedback == None:
            break
        if feedback.find(',') != -1 and feedback.find('.') != -1:
            # assume , for decimal
            feedback = feedback.replace('.', '')
        if feedback.find(',') != -1:
            feedback = feedback.replace(',', '.')
        try:
            feedback = float(feedback)
        except:
            print('I did not understand, please input a float')
        else:
            break
    return feedback

def input_string(text, regex='.*', default=''):
    while True:
        if default != '':
            text = text + ' [' + default + ']' 
        feedback = input_general(text)
        if feedback == None:
            break
        if feedback == '' and default != '':
            feedback = default
            break
        if not re.match(regex, feedback, re.IGNORECASE):
            print('Your input must match', regex)
        else:
            break
    return feedback

def input_yes(text, default='no'):
    feedback = input_string(text, 'yes|no', default=default)
    if feedback.lower() == 'yes':
        return True
    else:
        return False