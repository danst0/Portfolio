from django.test import TestCase
import datetime
from decimal import *
from transactions.models import Portfolio, Transaction
from securities.models import Security, Price
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