import datetime
from decimal import *

from django.utils import timezone
from django.test import TestCase

from transaction.models import Portfolio, Transaction
from securities.models import Security

# Create your tests here.

class TransactionTests(TestCase):
  def test_transaction_total_with_odd_values(self):
    """
    Adding Transaction should lead to correct total
    """
    time = timezone.now()
    sec = Security.objects.create(name='TestSec', aliases='Test Alias', isin_id='DETest', yahoo_id='ABC', type='Stock')
    pf = Portfolio('Test')
    transaction = Transaction.add(transaction_type='b', portfolio=pf, stock_id=sec, date=time, nominal=100, price=100, cost=100)
    self.assertEqual(transaction.total, Decimal(-9900))  
  def test_adding_transaction_with_future_date(self):
    """
    Adding Transaction with future date should return None
    """
    time = timezone.now() + datetime.timedelta(days=30)
    sec = Security.objects.create(name='TestSec', aliases='Test Alias', isin_id='DETest', yahoo_id='ABC', type='Stock')
    pf = Portfolio('Test')
    transaction = Transaction.add(transaction_type='b', portfolio=pf, stock_id=sec, date=time, nominal=100, price=100, cost=100, total=100)
    self.assertEqual(transaction, None)

