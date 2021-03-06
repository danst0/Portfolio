
from django.test import TestCase
import datetime
from securities.models import Security, Price, SecuritySplit
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

    def test_stock_splits_price(self):
        # import pdb; pdb.set_trace()
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
        result = price.get_prices(mysec)
        # print(result)
        self.assertEqual(result[0].price, Decimal('14.28571428571428571428571429'))

    def test_get_last_price_from_stock_id(self):
        sec = Security()
        price = Price()
        mysec = sec.add('Test', ['SomeAliasString'], '', 'APC.DE', 'Stock')
        time_0 = timezone.now() - datetime.timedelta(days=1)
        time_price_1 = timezone.now() - datetime.timedelta(days=5)
        time_price_2 = timezone.now() - datetime.timedelta(days=20)
        time_3 = timezone.now() - datetime.timedelta(days=25)
        price.add(mysec, time_price_1, 100)
        price.add(mysec, time_price_2, 50)
        # get_last_price_from_stock_id(self, stock_id, before_date=None, none_equals_zero=False, none_equals_oldest_available=False)

        result = price.get_last_price_from_stock_id(mysec)
        self.assertEqual(result, Decimal('100'))

        result = price.get_last_price_from_stock_id(mysec, time_price_2)
        self.assertEqual(result, Decimal('50'))

        result = price.get_last_price_from_stock_id(mysec, time_3)
        self.assertEqual(result, None)

        result = price.get_last_price_from_stock_id(mysec, time_3, none_equals_zero=True)
        self.assertEqual(result, Decimal('0'))

        result = price.get_last_price_from_stock_id(mysec, time_3, none_equals_zero=True, none_equals_oldest_available=True)
        self.assertEqual(result, Decimal('50'))

        result = price.get_last_price_from_stock_id(mysec, time_3, none_equals_oldest_available=True)
        self.assertEqual(result, Decimal('50'))

        result = price.get_last_price_from_stock_id(mysec, time_0)
        self.assertEqual(result, Decimal('100'))
