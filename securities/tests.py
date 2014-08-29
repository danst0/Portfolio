
from django.test import TestCase
import datetime
from decimal import *
from transactions.models import Portfolio, Transaction
from securities.models import Security, Price
from django.utils import timezone

# Create your tests here.


class PriceTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_import_historic_quotes(self):
        """Adding Transaction should lead to correct total"""
        sec = Security()
        sec.add('Test', '', '', 'APC.DE', 'Stock')
        p = Price()
        p.import_historic_quotes(years=0.5)
        date = timezone.now() - datetime.timedelta(days=30)
        price = p.get_last_price_from_stock_id(stock_id=sec.find('Test'), before_date=date)
        print(price)
        self.assertEqual(price, None)