#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import uuid
import os
import datetime
import time
import sys
import shutil


class Database:
    def __init__(self):
        sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes=b))
        sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes)
        self.data_path = os.path.expanduser('~') + '/Dropbox/'
        self.data_file = 'data.sql'
        self.backup(self.data_path, self.data_file)
        self.conn = sqlite3.connect(self.data_path + self.data_file,
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.c = self.conn.cursor()
        # Create tables
        try:
            self.c.execute(
                '''CREATE TABLE transactions (id GUID PRIMARY KEY, type TEXT, portfolio TEXT, stock_id GUID, date TEXT, nominal REAL, price REAL, cost REAL, total REAL)''')
        except:
            pass
        else:
            print('Created table for transactions')
        try:
            self.c.execute(
                '''CREATE TABLE stocks (id GUID PRIMARY KEY, name TEXT, aliases TEXT, isin_id TEXT, yahoo_id TEXT, type TEXT)''')
        except:
            pass
        else:
            print('Created table for stocks')
        try:
            self.c.execute('''CREATE TABLE prices (id GUID PRIMARY KEY, stock_id GUID, date TEXT, price REAL)''')
        except:
            pass
        else:
            print('Created table for prices')
        try:
            self.c.execute('''CREATE TABLE money (id GUID PRIMARY KEY, date TEXT, type TEXT, value REAL)''')
        except:
            pass
        else:
            print('Created table for money')

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()
        self.backup(self.data_path, self.data_file)

    def backup(self, path, file):
        files = []
        new_name = (path +
                    '.bak.' +
                    file +
                    '-' + datetime.datetime.fromtimestamp(os.path.getmtime(path + file)).strftime('%Y-%m-%d-%H-%M-%S'))
        shutil.copy(path + file, new_name)
        for file_name in os.listdir(path):
            if file_name.startswith('.bak.' + file):
                files.append(file_name)
        if len(files) > 10:
            os.remove(sorted(files)[0])