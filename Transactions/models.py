import uuid
from decimal import *

from django.db import models

from Securities.models import Security
from Securities.models import Price
from Transactions.Importer import CortalConsors


# from django.core.exceptions import ValidationError

# Create your models here.
class Portfolio(models.Model):
    name = models.CharField(max_length=200)

    def find(self, name):
        """
        Find securities
        :param name_alias_id:
        :return: ISIN_ID based on any (useful) information
        """
        find_something = Portfolio.objects.get(name=name)
        return None if not find_something else find_something
    def __str__(self):
        return 'Model:PF:' + str(self.name)


class Transaction(models.Model):
    # id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
    type = models.CharField(max_length=1)
    portfolio = models.ForeignKey(Portfolio)
    stock_id = models.ForeignKey(Security)
    date = models.DateField('date of transaction')
    nominal = models.DecimalField(max_digits=20, decimal_places=4)
    price = models.DecimalField(max_digits=20, decimal_places=4)
    cost = models.DecimalField(max_digits=20, decimal_places=4)
    total = models.DecimalField(max_digits=20, decimal_places=4)
    prices = Price()
    secs = Security()
    pf = Portfolio()

    def __str__(self):
        return ';'.join((
        str(self.portfolio), self.type, str(self.stock_id), str(self.date), str(self.nominal), str(self.price),
        str(self.cost), str(self.total)))

    def import_sources(self):
        i = CortalConsors()
        price_updates, transactions_update = i.read_pdfs()
        self.import_transactions(transactions_update)
        self.prices.import_prices(price_updates)

    def import_transactions(self, transaction_update):
        """

        :param transaction_update:
        [{'type': 'b', 'name': 'SGA DIV.STARS EUR.ZT04/UN', 'date': '2012-04-04', 'cost': 15.16, 'nominale': 45.0, 'value': 90.72}]
        :return:
        """
        #print(transaction_update)
        for trans in transaction_update:
            if trans:
                if trans['type'] == 'b':
                    total = -trans['nominale'] * trans['value'] - trans['cost']
                elif trans['type'] == 's':
                    total = trans['nominale'] * trans['value'] - trans['cost']
                elif trans['type'] == 'd':
                    total = trans['value']
                sec = self.secs.find(trans['name'])
                if not sec:
                    self.secs.add_stump(trans['name'])
                    sec = self.secs.find(trans['name'])
                pf = self.pf.find('All')
                if trans['type'] in ['b', 's']:
                    total = -trans['nominale'] * trans['value'] - trans['cost']
                    Transaction.objects.get_or_create(type=trans['type'],
                                                  portfolio=pf,
                                                  stock_id=sec,
                                                  date=trans['date'],
                                                  nominal=trans['nominale'],
                                                  price=trans['value'],
                                                  cost=trans['cost'],
                                                  total=total)
                else:
                    Transaction.objects.get_or_create(type=trans['type'],
                                                  portfolio=pf,
                                                  stock_id=sec,
                                                  date=trans['date'],
                                                  nominal=0.0,
                                                  price=trans['value'],
                                                  cost=0.0,
                                                  total=total)

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
        total = Decimal(0)
        if stock_id:
            for item in Transaction.objects.filter(portfolio__name=portfolio,
                                                     type=type,
                                                     date__range=[from_date, to_date],
                                                     stock_id=stock_id):
                total += item.total
        else:
            for item in Transaction.objects.filter(portfolio__name=portfolio,
                                                     type=type,
                                                     date__range=[from_date, to_date]):
                total += item.total
        return total


    def get_stocks_in_portfolio(self, portfolio, date):
        """Get portfolio contents on that specific date, incl. all transactions from that date"""
        result = Transaction.objects.filter(portfolio__name=portfolio, type='b',
                                            date__lte=date) | Transaction.objects.filter(portfolio__name=portfolio,
                                                                                         type='s', date__lte=date)
        stocks = {}
        for item in result:
            if item.id not in stocks.keys():
                stocks[item.id] = Decimal(0)
            stocks[item.id] = stocks[item.id] + item.nominal
        return stocks

    def get_total_for_portfolio(self, portfolio):
        """NOT YET FINAL"""
        result = Transaction.objects.filter(portfolio__name=portfolio)
        aggregate = {}
        # self.data.c.execute('''SELECT name, SUM(nominal), SUM(cost), SUM(total) FROM transactions INNER JOIN stocks ON stocks.id = transactions.stock_id WHERE portfolio = ? GROUP BY stock_id''', (portfolio,)).fetchall()
        # #		for item in result
        return result


        #	def add(self, type, stock_id, date, nominal, price, cost, portfolio):
        #		if stock_id != None:
        #			if price < 0:
        #				price = -1 * price
        #			if cost < 0:
        #				cost = -1 * cost
        #			if type == 'b':
        #				if nominal < 0:
        #					nominal = -1 * nominal
        #				total = -1 * price * nominal - cost
        #			elif type == 's':
        #				if nominal > 0:
        #					nominal = -1 * nominal
        #				total = -1 * price * nominal + cost
        #			elif type == 'd':
        #				if nominal != 0:
        #					price = price * nominal
        #					nominal = 0
        #				cost = 0
        #				total = price
        #			result = self.data.c.execute('''SELECT id FROM transactions WHERE type = ? AND portfolio = ? AND stock_id = ? AND date = ? AND nominal = ? AND price = ? AND cost = ? AND total = ?''', (type, portfolio, stock_id, date, nominal, price, cost, total)).fetchall()
        #
        #			if result == []:
        #				self.data.c.execute('INSERT INTO transactions (id, type, portfolio, stock_id, date, nominal, price, cost, total) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (uuid.uuid4(), type, portfolio, stock_id, date, nominal, price, cost, total))
        #				self.money.update('settlement', date, total)
        #				if type != 'd' and price != 0.0:
        #					self.prices.update(self.secs.get_isin_id_from_stock_id(stock_id), date, price)
        #				print('Cash addition ' + str(total))
        #				return True
        #			else:
        #				print('Transaction already seems to exist: ' + str(result))
        #				return False
        #		else:
        #			return False
        # #		  self.data.commit()