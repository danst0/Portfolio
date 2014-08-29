
from django.test import TestCase
import datetime
from securities.models import Security, Price
from decimal import *

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
        sec.add('Test', '', '', 'APC.DE', 'Stock')
        p = Price()
        p.import_historic_quotes(years=0.5)
        date = datetime.datetime.strptime('01.08.2014', '%d.%m.%Y')
        price = p.get_last_price_from_stock_id(stock_id=sec.find('Test'), before_date=date)
        self.assertEqual(price.price, Decimal('70.93'))