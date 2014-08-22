#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import re
import datetime
#from Securities.models import Security
#from Transactions.models import Transaction


class Importer:
    def __init__(self):
        self.base_path = os.path.expanduser('~') + '/Desktop/PDFs'
#        self.secs = Security()
#        self.transaction = Transaction()
        print(self.base_path)

class CortalConsors(Importer):
    def read_pdfs(self):
        file_counter = 0
        price_updates = []
        transactions_update = []
        for file in os.listdir(self.base_path):
            if file.startswith('PERSONAL') and file.endswith('.pdf'):
                print('Import ' + file)
                subprocess.check_output(
                    ['/usr/local/bin/pdftotext', '-nopgbrk', '-eol', 'unix', '-table', self.base_path + '/' + file,
                     self.base_path + '/data.txt'])
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
                data = self.get_data_from_text(
                    subprocess.check_output(['/usr/local/bin/pdf2txt.py', self.base_path + '/' + file]).decode("utf-8"))
                transactions_update.append(data)
            os.remove(self.base_path + '/' + file)
#        print(file_counter, 'files successfully imported.')
        return price_updates, transactions_update

    def get_data_from_text(self, text):
        valid = False
        type = ''
        line_counter = 0
        lines = text.split('\n')
        print_all = False
        total_value = None
        currency = ''
        value = 0.0
        wert_found = False
        charge = 0.0
        while line_counter < len(lines):
            line = lines[line_counter]
            if (line.find('Daniel Dumke') != -1 or
                        line.find('Daniel Stengel') != -1):
                valid = True
                # print('Valid document for Daniel Dumke')
            if valid:
                if type == '':
                    if line.find('DIVIDENDENGUTSCHRIFT ') != -1:
                        type = 'dividende'
                    elif line.find('ERTRAGSGUTSCHRIFT') != -1:
                        type = 'dividende'
                    elif line.find('WERTPAPIERABRECHNUNG') != -1:
                        # print_all = True
                        line_counter += 1
                        line = lines[line_counter]
                        if line.find('KAUF') != -1:
                            type = 'kauf'
                        elif line.find('VERKAUF') != -1:
                            type = 'verkauf'
                else:
                    if line.find('WKN') != -1:
                        # print(line)
                        try:
                            wkn = re.match('.*WKN.*([A-Z0-9]{6}).*', line).group(1)
                        except:
                            pass
                        else:
                            #							  print(wkn)
                            line_counter += 1
                            line = lines[line_counter]
                            name = line.strip(' ')
                    elif line.find('UMGER.ZUM DEV.-KURS') != -1:
                        # Will be overwritten if WERT Line is found (and correct)
                        # print(line)
                        result = re.match('UMGER.ZUM DEV.-KURS\s.*([A-Z]{3})\s*([0-9\.,]*)', line)
                        currency = result.group(1)
                        if currency != 'EUR':
                            print('Error while importing, currency not EUR')
                            sys.exit()
                        value = float(result.group(2).replace('.', '').replace(',', '.'))
                        wert_found = True
                    elif line.find('WERT') != -1:
                        # print(line)
                        #						  pdb.set_trace()
                        result = re.match('WERT\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4}).*([A-Z]{3})\s*([0-9\.,]*)', line)
                        if not result:
                            result = re.match('WERT\s*([0-9]{2}\.[0-9]{2}\.[0-9]{4})', line)
                        date = datetime.datetime.strptime(result.group(1), "%d.%m.%Y").date()
                        if currency == '':
                            currency = result.group(2)
                        if currency != 'EUR':
                            print('Error while importing, currency not EUR')
                            sys.exit()
                        try:
                            value = float(result.group(3).replace('.', '').replace(',', '.'))
                        except:
                            if value == 0.0:
                                print('Error while importing values')
                                sys.exit()
                        wert_found = True
                        # print(date, currency, value)
                    #						  print(result)

                    elif line.find('Umsatz') != -1:
                        # Nominale when buying
                        # print(line)
                        line_counter += 1
                        line = lines[line_counter]
                        #						  print(line)
                        nominale = float(line.replace(',', '.'))
                        # print(nominale)
                    elif line == 'Wertpapier':
                        # Nominale when buying
                        # print(line)
                        line_counter += 1
                        line = lines[line_counter]
                        name = line.strip(' ')
                        result = re.match('0,0.%.(.*?)00.*', name)
                        if result:
                            name = result.group(1).strip()
                        #						  print(name)

                    elif re.match('AM.*([0-9\.]{10}).*UM.*', line) != None:
                        date = re.match('AM.*([0-9\.]{10}).*UM.*', line).group(1)
                        date = datetime.datetime.strptime(date, "%d.%m.%Y").date()
                        # print(date)
                    elif line == 'Kurs':
                        # Nominale when buying
                        # print(line)
                        line_counter += 2
                        line = lines[line_counter]
                        #						  print(line)
                        value = float(line.split(' ')[0].replace(',', '.'))
                        #						  print(value)
                        total_value = value * nominale
                        # print(total_value)
                    #						  print('total value ', total_value)
                    #						  print_all = True
                    elif line.replace('.', '').find(str(total_value).replace('.', ',')) != -1:
                        # Nominale when buying
                        # All additional lines
                        while lines[line_counter + 2] != '':
                            # print(line)
                            line_counter += 1
                            line = lines[line_counter]
                            charge += float(line.replace('.', '').replace(',', '.'))
                            # print(charge)
                        line_counter += 1
                        line = lines[line_counter]
                        # print(line)
                        total = float(line.replace('.', '').replace(',', '.'))
                        #						  print(total)
                        #						  print(total_value + charge, total)
                        #						  print(abs(total - (total_value + charge)))
                        #						  print(lines[line_counter+1])
                        #						  print(lines[line_counter+2])
                        #						  print(lines[line_counter+3])
                        if abs(total - (total_value + charge)) > 0.01:
                            print('Error while importing, totals do not match')
                            sys.exit()
                        #						  print(line)
                        #			  if print_all:
                        #			  print(line.replace('.', ''))
            line_counter += 1
        if not valid:
            return None
        elif type == 'dividende':
            return {'type': 'd', 'name': name, 'date': date.strftime('%Y-%m-%d'), 'value': value}
        elif type == 'kauf':
            return {'type': 'b', 'name': name, 'date': date.strftime('%Y-%m-%d'), 'nominale': nominale, 'value': value,
                    'cost': charge}
        elif type == 'verkauf':
            return {'type': 's', 'name': name, 'date': date.strftime('%Y-%m-%d'), 'nominale': nominale, 'value': value,
                    'cost': charge}

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
                        name_date_price.append(
                            (table_line.group(3), table_line.group(6), float(table_line.group(5).replace(',', '.'))))
                    #						print(table_line.group(3), table_line.group(5), table_line.group(6))
                    if line.lower().find('WERTENTWICKLUNG FÜR IHR DEPOT'.lower()) != -1:
                        found_start = False
                elif line.lower().find('IHR DEPOT (ALPHABETISCH GEORDNET)'.lower()) != -1:
                    #					print('HEUREKA')
                    found_start = True
            line_counter += 1
        return name_date_price