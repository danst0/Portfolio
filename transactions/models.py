import uuid
from decimal import *

from django.db import models

from securities.models import Security
from securities.models import SecuritySplit
from securities.models import Price
from transactions.Importer import CortalConsors
from django.utils import timezone
import datetime

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
        find_something = Portfolio.objects.get_or_create(name=name)[0]
        return find_something
    def __str__(self):
        return 'Model:PF:' + str(self.name)


class Transaction(models.Model):
    # id = models.CharField(max_length=100, blank=True, unique=True, default=uuid.uuid4)
    transaction_type = models.CharField(max_length=1)
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
        str(self.portfolio), self.transaction_type, str(self.stock_id), str(self.date), str(self.nominal), str(self.price),
        str(self.cost), str(self.total)))

    def import_sources(self):
        i = CortalConsors()
        price_updates, transactions_update = i.read_pdfs()
        self.import_transactions(transactions_update)
        self.prices.import_prices(price_updates)

    def import_transactions(self, transaction_update):
        for trans in transaction_update:
            if trans:
                sec = self.secs.find(trans['name'])
                if not sec:
                    self.secs.add_stump(trans['name'])
                    sec = self.secs.find(trans['name'])
                pf = self.pf.find('All')
                self.add(transaction_type=trans['type'],
                         portfolio=pf,
                         stock_id=sec,
                         date=trans['date'],
                         nominal=trans['nominal'],
                         price=trans['value'],
                         cost=trans['cost'])


    def add(self, transaction_type, portfolio, stock_id, date, nominal, price, cost):
        nominal = abs(nominal)
        price = abs(price)
        cost = abs(cost)
        if transaction_type == 'b':
            total = -(nominal * price) - cost
        elif transaction_type == 's':
            total = (nominal * price) - cost
        elif transaction_type == 'd':
            total = price
            nominal = Decimal(0)
            cost = Decimal(0)
        else:
            raise NameError('Not a valid transaction type (' + str(transaction_type) +')')
        #import pdb; pdb.set_trace()

        if not isinstance(date, datetime.datetime):
            now = timezone.now().date()
        else:
            now = timezone.now()
        if date > now:
            raise NameError('Date in the future (' + str(date) +')')

        t = Transaction.objects.get_or_create(transaction_type=transaction_type,
                                              portfolio=portfolio,
                                              stock_id=stock_id,
                                              date=date,
                                              nominal=nominal,
                                              price=price,
                                              cost=cost,
                                              total=total)
        if len(t) > 0:
            return t[0]


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

    def get_total(self, portfolio, transaction_type, from_date, to_date, stock_id=None):
        total = Decimal(0)
        if stock_id:
            for item in Transaction.objects.filter(portfolio__name=portfolio,
                                                   transaction_type=transaction_type,
                                                   date__range=[from_date, to_date],
                                                   stock_id=stock_id):
                total += item.total
        else:
            for item in Transaction.objects.filter(portfolio__name=portfolio,
                                                   transaction_type=transaction_type,
                                                   date__range=[from_date, to_date]):
                total += item.total
        return total


    def get_stocks_in_portfolio(self, portfolio, date):
        """Get portfolio contents on that specific date, incl. all transactions from that date"""
        result = Transaction.objects.filter(portfolio__name=portfolio,
                                            transaction_type='b',
                                            date__lte=date) |\
                 Transaction.objects.filter(portfolio__name=portfolio,
                                            transaction_type='s',
                                            date__lte=date)
        stocks = {}
        for item in result:
            if item.id not in stocks.keys():
                stocks[item.id] = Decimal(0)
            stocks[item.id] = stocks[item.id] + item.nominal
        return stocks

    def rectify_nominal_with_stock_split(self, stock_id, stock_date, nominal):
        ss = SecuritySplit()
        splits = ss.get_splits(stock_id)
        if splits:
            for split in splits:
                if stock_date < split.date:
                    nominal = nominal * split.ratio
        return nominal

    def get_total_for_portfolio(self, portfolio, date):
        result = Transaction.objects.filter(portfolio__name=portfolio, date__lte=date)
        per_stock = {}
        for item in result:
            if item.stock_id not in per_stock.keys():
                per_stock[item.stock_id] = {'nominal': self.rectify_nominal_with_stock_split(item.stock_id,
                                                                                             item.date,
                                                                                             item.nominal),
                                            'cost': item.cost,
                                            'total': item.total}
            else:
                per_stock[item.stock_id]['nominal'] += self.rectify_nominal_with_stock_split(item.stock_id,
                                                                                             item.date,
                                                                                             item.nominal)
                per_stock[item.stock_id]['cost'] += item.cost
                per_stock[item.stock_id]['total'] += item.total
        return per_stock

    def list_pf(self, portfolio, from_date, to_date):
        stock_at_beginning = self.get_total_for_portfolio(portfolio, from_date)
        stocks_at_end = self.get_total_for_portfolio(portfolio, to_date)
        values = []
        total_value = Decimal(0)
        total_profit = Decimal(0)
        for key in sorted(stocks_at_end.keys(), key=lambda x: x.name):
            price_at_beginning = self.prices.get_last_price_from_stock_id(key, from_date)
            price_at_end = self.prices.get_last_price_from_stock_id(key, to_date)
            value_at_beginning = Decimal(0)
            value_at_end = Decimal(0)
            if price_at_beginning and key in stock_at_beginning.keys():
                value_at_beginning = stock_at_beginning[key]['nominal'] * price_at_beginning
            if price_at_end:
                value_at_end = stocks_at_end[key]['nominal'] * price_at_end

            values.append({'name': key.name,
                           'nominal': stocks_at_end[key]['nominal'],
                           'cost': stocks_at_end[key]['cost'],
                           'price': price_at_end,
                           'value_at_beginning': value_at_beginning,
                           'value_at_end': value_at_end,
                           'profit': value_at_end-value_at_beginning})
            total_value += value_at_end
            total_profit += value_at_end - value_at_beginning
        values.append({'name': 'Total', 'value_at_end': total_value, 'profit': total_profit})
        return values