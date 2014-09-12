#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import re
import datetime
import sys
#from Securities.models import Security
#from Transactions.models import Transaction
from decimal import *


class Importer:
    def __init__(self):
        self.base_path = os.path.expanduser('~') + '/Desktop/PDFs'
#        self.secs = Security()
#        self.transaction = Transaction()
        print(self.base_path)

def make_float(str):
    return str.replace('.', '').replace(',','.')

class CortalConsors(Importer):
    def read_pdfs(self):
        file_counter = 0
        price_updates = []

        for file in os.listdir(self.base_path):
            if file.startswith('PERSONAL') and file.endswith('.pdf'):
                print('Import ' + file)
                try:
                    subprocess.check_output(
                    ['/usr/local/bin/pdftotext', '-nopgbrk', '-eol', 'unix', '-table', self.base_path + '/' + file,
                     self.base_path + '/data.txt'])
                except:
                    print('Error while importing.')
                    data = None
                else:
                    with open(self.base_path + '/data.txt', 'rb') as myfile:
                        data = myfile.read()
                    data = self.get_data_from_personal_investment_report(data)
                if data:
                    price_updates.append(data)
                    file_counter += 1
                os.remove(self.base_path + '/' + file)
        try:
            os.remove(self.base_path + '/data.txt')
        except:
            pass
        transactions_update = []
        for file in os.listdir(self.base_path):
            if (file.startswith('HV-BEGLEIT') or
                    file.startswith('KONTOABSCH') or
                    file.startswith('KONTOAUSZU') or
                    file.startswith('PERSONAL') or
                    file.startswith('TERMINANSC') or
                    file.startswith('WICHTIGE_M') or
                    file.startswith('VERLUSTVER') or
                    file.startswith('VERTRAGSRE')):
                # Remove invalid PDFs
                print('Ignore ' + file)
                os.remove(self.base_path + '/' + file)
            elif file.endswith('.pdf'):
                print('Import ' + file)
                try:
                    subprocess.check_output(
                    ['/usr/local/bin/pdftotext', '-nopgbrk', '-eol', 'unix', '-table', self.base_path + '/' + file,
                     self.base_path + '/data.txt'])
                except:
                    print('Error while importing.')
                    data = None
                else:
                    with open(self.base_path + '/data.txt', 'rb') as myfile:
                        data = myfile.read()
                    data = self.get_data_from_text(data)
                    if data:
                        transactions_update.append(data)
                        file_counter += 1
                    os.remove(self.base_path + '/' + file)
            try:
                os.remove(self.base_path + '/data.txt')
            except:
                pass
#        print(file_counter, 'files successfully imported.')
        return price_updates, transactions_update

    def get_data_from_text(self, text):
        valid = False
        type = ''
        # lines = text.split('\n')
        lines = text.decode('latin-1').splitlines()
        # print(lines)
        new_lines = []
        for line in lines:
            if line != '':
                new_lines.append(line)
        lines = '\n'.join(new_lines)
        # print(lines)
        total_value = Decimal(0)
        total = Decimal(0)
        value = Decimal(0)
        charge = Decimal(0)
        result = re.search('daniel\s(stengel|dumke)', lines, re.IGNORECASE)
        error = 0
        if result:
            if lines.lower().find('dividendengutschrift ') != -1:
                type = 'dividende'
            elif lines.lower().find('ertragsgutschrift') != -1:
                type = 'dividende'
            elif lines.lower().find('wertpapierabrechnung') != -1:
                if lines.lower().find('kauf') != -1:
                    type = 'kauf'
                elif lines.lower().find('verkauf') != -1:
                    type = 'verkauf'
            # import pdb; pdb.set_trace()
            result = re.search('wertpapier\s{1,100}wkn\s{1,100}isin.*?\n([%,/A-Z\.\s\-0-9]{5,35})\s{3}[\s0\.]{1,100}([A-Z0-9]{6})\s{3}\s{1,100}([A-Z]{2}[A-Z0-9]{10})', lines, re.DOTALL | re.IGNORECASE)
            if result:
                name = result.group(1)
                wkn = result.group(2)
                isin = result.group(3)
            else:
                print('No name/wkn/isin found')
                error += 1

            result = re.search('ST\s{1,20}([0-9]{1,6},[0-9]{5}).*Kurs\s{1,20}([0-9]{1,6},[0-9]{6})', lines, re.DOTALL)
            if result:
                nominale = Decimal(make_float(result.group(1)))
                value = Decimal(make_float(result.group(2)))
            else:
                print('No nominale/value found')
                error += 1

            result = re.search('KAUF\s{1,40}AM\s([0-9]{2}\.[0-9]{2}\.[0-9]{4})\s{1,20}UM', lines)
            if result:
                date = datetime.datetime.strptime(result.group(1), "%d.%m.%Y").date()
            else:
                print('No date found')
                error += 1

            result = re.search('Kurswert\s{1,}EUR\s{1,}([0-9\.]{1,8},[0-9]{2})', lines)
            if result:
                total_value = Decimal(make_float(result.group(1)))
                if total_value != nominale * value:
                    print('Error while importing, total value does not match')

            else:
                print('No total value found')
                error += 1


            result = re.search('Kurswert.*?([0-9\.]{1,8},[0-9]{2}).*?Wert.*?([0-9\.]{1,8},[0-9]{2})', lines, re.DOTALL)
            if result:
                total = Decimal(make_float(result.group(2)))
                charge = total - total_value
            else:
                print('No charge found')
                error += 1

            if abs(total - (total_value + charge)) != 0:
                print('Error while importing, totals do not match')
                error += 1



            if error == 0:
                if type == 'dividende':
                    return {'type': 'd', 'name': name, 'date': date, 'nominal': Decimal(0), 'value': value,
                            'cost': Decimal(0)}
                elif type == 'kauf':
                    return {'type': 'b', 'name': name, 'date': date, 'nominal': nominale, 'value': value,
                            'cost': charge}
                elif type == 'verkauf':
                    return {'type': 's', 'name': name, 'date': date, 'nominal': nominale, 'value': value,
                            'cost': charge}
        return None

    def get_data_from_personal_investment_report(self, text):
        valid = False
        line_counter = 0
        # print(text)
        lines = text.decode('latin-1').splitlines()
        #		print(lines)
        found_start = False
        name_date_price = []

        while line_counter < len(lines):
            line = lines[line_counter]
            #			print(line)
            if (line.lower().find('daniel dumke') != -1 or
                        line.lower().find('daniel stengel') != -1):
                valid = True
            if valid:
                #				print(line)
                #				print('valid')
                #				print(found_start)
                if found_start:
                    #					print(line)
                    table_line = re.match(
                        '([0-9\.]{1,7},[0-9]{2}\s*)([A-Z0-9]{6})\s*(.*?)\s{2,}([0-9,]*)\s{2,}([0-9,]*)\s{2,}([0-9]{2}.[0-9]{2}.[0-9]{4})',
                        line)
                    if table_line:
                        sec_name = table_line.group(3)
                        sec_price = Decimal(table_line.group(5).replace(',', '.'))
                        sec_date = datetime.datetime.strptime(table_line.group(6), '%d.%m.%Y')
                        name_date_price.append((sec_name, sec_date, sec_price))
                    if line.lower().find('WERTENTWICKLUNG FÜR IHR DEPOT'.lower()) != -1:
                        found_start = False
                elif line.lower().find('IHR DEPOT (ALPHABETISCH GEORDNET)'.lower()) != -1:
                    #					print('HEUREKA')
                    found_start = True
            line_counter += 1
        return name_date_price