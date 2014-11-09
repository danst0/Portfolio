from django.test import TestCase
import datetime
from decimal import *
from transactions.models import Portfolio, Transaction
from securities.models import Security, Price, SecuritySplit
from django.utils import timezone

# Create your tests here.


class TransactionTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_transaction_total_with_odd_values(self):
        """Adding Transaction should lead to correct total"""
        time = timezone.now().date()
        sec = Security.objects.create(name='TestSec', aliases='Test Alias', isin_id='DETest', yahoo_id='ABC',
                                      type='Stock')
        pf = Portfolio.objects.create(name='Test')
        t = Transaction()
        transaction = t.add('b', pf, sec, time, 100, 100, 100)
        self.assertEqual(transaction.total, Decimal(-10100))

    def test_adding_transaction_with_future_date(self):
        """Adding Transaction with future date should return None"""
        time = timezone.now().date() + datetime.timedelta(days=30)
        sec = Security.objects.create(name='TestSec', aliases='Test Alias', isin_id='DETest', yahoo_id='ABC',
                                      type='Stock')
        pf = Portfolio.objects.create(name='Test')
        t = Transaction()
        self.assertRaises(NameError, t.add, 'b', pf, sec, time, 100, 100, 100)

    def a_test_portfolio_overview(self):
        sec = Security.objects.create(name='TestSec', aliases='Test Alias', isin_id='DETest', yahoo_id='ABC',
                                      type='Stock')
        pf = Portfolio.objects.create(name='Test')
        t = Transaction()
        time = timezone.now().date()
        p = Price()
        p.add(sec, time, Decimal(111))
        t.add('b', pf, sec, time, 100, 100, 100)

        p = t.list_pf(pf.name, time)
        self.assertEqual(p, [{
                                 'nominal': Decimal('100'),
                                 'invest': Decimal('-10100'),
                                 'profit': Decimal('1000'),
                                 'name': 'TestSec',
                                 'value': Decimal('11100'),
                                 'price': Decimal('111'),
                                 'cost': Decimal('100')},
                             {
                                 'name': 'Total',
                                 'value': Decimal('11100')}])

    def test_stock_splits_quantity(self):

        pf = Portfolio.objects.create(name='Test')
        sec = Security()
        price = Price()
        mysec = sec.add('Test', ['SomeAliasString'], '', 'APC.DE', 'Stock')
        split = SecuritySplit()
        time_price_1 = timezone.now() - datetime.timedelta(days=20)
        time_split = timezone.now() - datetime.timedelta(days=10)
        time_price_2 = timezone.now() - datetime.timedelta(days=5)
        price.add(mysec, time_price_1, 100)
        price.add(mysec, time_price_2, 15)
        split.add(mysec, time_split, 7)
        t = Transaction()
        t.add('b', pf, mysec, time_price_1, 100, 100, 100)
        t.add('b', pf, mysec, time_split, 90, 100, 100)
        t.add('b', pf, mysec, time_price_2, 80, 100, 100)

        result = t.get_total_for_portfolio(pf.name, time_price_1)
        # print(result[mysec]['nominal'])
        self.assertEqual(result[mysec]['nominal'], Decimal('700'))

        # import pdb; pdb.set_trace()
        result = t.get_total_for_portfolio(pf.name, time_split)
        # print(result[mysec]['nominal'])
        self.assertEqual(result[mysec]['nominal'], Decimal('790'))

        result = t.get_total_for_portfolio(pf.name, time_price_2)
        # print(result[mysec]['nominal'])
        self.assertEqual(result[mysec]['nominal'], Decimal('870'))
