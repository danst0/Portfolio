from django.db import models
from core.helper_functions import Helper
import datetime

# Create your models here.
class Security(models.Model):
    name = models.CharField(max_length=200)
    aliases = models.CharField(max_length=400)
    isin_id = models.CharField(max_length=10)
    yahoo_id = models.CharField(max_length=10)
    type = models.CharField(max_length=10)

    search_fields = ['name', 'aliases']

    def set_aliases(self, x):
        if x and not isinstance(x, str):
            self.aliases = ':::'.join(x)
        else:
            self.aliases = ''

    def get_aliases(self):
        if self.aliases == '':
            return []
        else:
            return self.aliases.split(':::')

    def find(self, name_alias_id):
        """
        Find securities
        :param name_alias_id:
        :return: ISIN_ID based on any (useful) information
        """
        find_something = Security.objects.filter(name=name_alias_id) |\
                         Security.objects.filter(aliases__contains=name_alias_id) |\
                         Security.objects.filter(isin_id=name_alias_id) |\
                         Security.objects.filter(yahoo_id=name_alias_id)
        return None if not find_something else find_something[0]
    def add(self, name, aliases, isin_id, yahoo_id, type):
        Security.objects.create(name=name, aliases=aliases, isin_id=isin_id, yahoo_id=yahoo_id, type=type)
    def add_stump(self, name=None, aliases=None, isin_id=None, yahoo_id=None, type=None):
        unavailable = 'unknown' + Helper.rand_str()
        if not name:
            name = unavailable
        if not aliases:
            aliases = []
        if not isin_id:
            isin_id = unavailable
        if not yahoo_id:
            yahoo_id = unavailable
        if not type:
            type = unavailable
        self.add(name, aliases, isin_id, yahoo_id, type)
    def __str__(self):
        return self.name



class Price(models.Model):
    stock_id = models.ForeignKey(Security)
    date = models.DateField('date of price')
    price = models.DecimalField(max_digits=20, decimal_places=4)
    securities = Security()

    def import_prices(self, price_updates):
        for file in price_updates:
            for name, date, price in file:
                date = datetime.datetime.strptime(date, '%d.%m.%Y').strftime('%Y-%m-%d')
                #print(name, date, price)
                sec = self.securities.find(name)
                if not sec:
                    self.securities.add_stump(name)
                    sec = self.securities.find(name)
                Price.objects.create(stock_id=sec, date=date, price=price)

    def __str__(self):
        return self.stock_id, self.date, self.price
