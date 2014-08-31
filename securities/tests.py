
from django.test import TestCase
import datetime
from securities.models import Security, Price, SecuritySplits
from decimal import *
from django.utils import timezone

# Create your tests here.


class PriceTests(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_import_historic_quotes(self):
        """
        Adding Transaction should lead to correct total
        Test only works as long as we scrape enough years (or date is recent enough)!!!
        """
        sec = Security()
        mysec = sec.add('Test', '', '', 'APC.DE', 'Stock')
        p = Price()
        p.import_historic_quotes(years=0.5)
        date = datetime.datetime.strptime('01.08.2014', '%d.%m.%Y')
        price = p.get_last_price_from_stock_id(mysec, date)
        self.assertEqual(price, Decimal('70.93'))

    def test_assignment_of_str_as_alias(self):
        sec = Security()
        sec.add('Test', 'SomeAliasString', '', 'APC.DE', 'Stock')
        result = Security.objects.get(name='Test')
        self.assertEqual(result.aliases, '')

    def test_assignment_of_str_with_token_as_alias(self):
        sec = Security()
        sec.add('Test', 'SomeAliasString:::', '', 'APC.DE', 'Stock')
        result = Security.objects.get(name='Test')
        self.assertEqual(result.aliases, 'SomeAliasString')

    def test_assignment_of_alias(self):
        sec = Security()
        sec.add('Test', ['SomeAliasString'], '', 'APC.DE', 'Stock')
        result = Security.objects.get(name='Test')
        self.assertEqual(result.aliases, 'SomeAliasString')

    def test_stock_splits(self):
        sec = Security()
        price = Price()
        sec.add('Test', ['SomeAliasString'], '', 'APC.DE', 'Stock')
        split = SecuritySplits()
        time_price_1 = timezone.now() - datetime.timedelta(days=20)
        time_split = timezone.now() - datetime.timedelta(days=10)
        time_price_2 = timezone.now() - datetime.timedelta(days=5)
        price.add(sec, time_price_1, 100)
        price.add(sec, time_price_2, 15)
        split.add(sec, time_split, 7)
        result = price.get_prices(sec)
        self.assertEqual(result, 'SomeAliasString')
