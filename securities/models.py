from django.db import models
from core.helper_functions import Helper
import datetime
from django.utils import timezone
import urllib.request
import re
from decimal import Decimal
import ystockquote
import urllib
import jellyfish
import logging
import os

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)



class ListField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ':::')
        kwargs['max_length'] = 400
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        result = value.split(self.token)
        try:
            result = result.remove('')
        except ValueError:
            pass
        return result

    def get_prep_value(self, value):
        # print('value', value)
        if isinstance(value, list) or isinstance(value, tuple):
            value = self.token.join(value)
        elif value.find(':::') != -1:
            value = value.strip(':::')
        else:
            value = ''
        # print('newval', value)
        return value

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


# Create your models here.
class Security(models.Model):
    name = models.CharField(max_length=200)
    aliases = ListField(blank=True, null=True)
    isin_id = models.CharField(max_length=12)
    yahoo_id = models.CharField(max_length=12)
    type = models.CharField(max_length=10)

    search_fields = ['name', 'aliases']

    def find(self, name_alias_id, fuzzy=False):
        """
        Find securities
        :param name_alias_id:
        :return: ISIN_ID based on any (useful) information
        """
        # import pdb; pdb.set_trace()
        if not fuzzy:
            find_something = Security.objects.filter(name__contains=name_alias_id) |\
                             Security.objects.filter(aliases__contains=name_alias_id) |\
                             Security.objects.filter(isin_id=name_alias_id) |\
                             Security.objects.filter(yahoo_id=name_alias_id)
            result = None if not find_something else find_something[0]
        else:
            # import pdb; pdb.set_trace()
            min_score = 2.5
            min_score_sec = None
            # print('Trans', name_alias_id)
            for sec in Security.objects.all():
                if not isinstance(sec.aliases, list):
                    all_names = [sec.name]
                else:
                    all_names = sec.aliases + [sec.name]
                for alias in all_names:
                    # print('analyzing sec', alias)
                    score = jellyfish.damerau_levenshtein_distance(name_alias_id.lower(), alias.lower())
                    # print('Score', score)
                    if score < min_score:
                        min_score = score
                        min_score_sec = sec
            result = min_score_sec, min_score

            # >>> jellyfish.levenshtein_distance('jellyfish', 'smellyfish')
            # 2
            # >>> jellyfish.jaro_distance('jellyfish', 'smellyfish')
            # 0.89629629629629637
            # >>> jellyfish.damerau_levenshtein_distance('jellyfish', 'jellyfihs')
            # 1
        return result

    def add(self, name, aliases, isin_id, yahoo_id, type):
        return Security.objects.get_or_create(name=name, aliases=aliases, isin_id=isin_id, yahoo_id=yahoo_id, type=type)[0]

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

    def __init__(self, *args, **kwargs):
        self.securities = Security()
        self.securitysplit = SecuritySplit()
        super().__init__(*args, **kwargs)
        self.base_path = os.path.expanduser('~') + '/Desktop/PDFs'

    def get_dates_and_prices(self, stock_id, from_date, to_date):
        result = Price.objects.filter(stock_id=stock_id, date__gte=from_date, date__lte=to_date).order_by('date')

        # Redo with map function
        # result.order_by('date')
        ss = SecuritySplit()
        splits = ss.get_splits(stock_id)
        if splits:
            new_prices = []
            for split in splits:
                for price in result:
                    if price.date < split.date:
                        price.price = price.price / split.ratio
                    new_prices.append(price)
            result = new_prices

        dates = []
        values = []

        for price in result:
            dates.append(price.date)
            values.append(price.price)
        # import pdb; pdb.set_trace()
        return dates, values


    def import_prices(self, price_updates):
        output = []
        for file in price_updates:
            for name, date, price in file:
                sec = self.securities.find(name)
                if not sec:
                    self.securities.add_stump(name)
                    sec = self.securities.find(name)
                    output.append({'name': sec.name, 'status': 'Created stock'})
                p = Price.objects.filter(stock_id=sec, date=date, price=price)
                if not p:
                    Price.objects.create(stock_id=sec, date=date, price=price)
                    output.append({'name': sec.name, 'date': date, 'price': price, 'status': 'Newly created'})
        if len(output) == 0:
            output.append({'name': '', 'status': 'No prices had to be added'})
        return output

    def __str__(self):
        return str(self.stock_id) + str(self.date) + str(self.price)

    def get_prices(self, stock_id, before_date=None, order_by_date=False):
        # import pdb; pdb.set_trace()
        if before_date:
            result = Price.objects.filter(stock_id=stock_id, date__lte=before_date)
        else:
            result = Price.objects.filter(stock_id=stock_id)
        if order_by_date:
            result = result.order_by('-date')
        ss = SecuritySplit()
        splits = ss.get_splits(stock_id)
        if splits:
            new_prices = []
            for split in splits:
                for price in result:
                    if price.date < split.date:
                        price.price = price.price / split.ratio
                    new_prices.append(price)
            result = new_prices
        return result

    def get_last_price(self, isin_id, before_date=None, none_equals_zero=False):
        stock_id = self.secs.get_stock_id_from_isin_id(isin_id)
        return self.get_last_price_from_stock_id(stock_id, before_date, none_equals_zero)

    def get_last_price_from_stock_id(self, stock_id, before_date=None, none_equals_zero=False, none_equals_oldest_available=False):
        """Return last price available, if given, return last price available before given date"""
        prices = self.get_prices(stock_id, before_date, order_by_date=True)
        no_price = False
        if prices:
            return prices[0].price
        else:
            if none_equals_oldest_available:
                prices = self.get_prices(stock_id, order_by_date=True)
                if prices:
                    return prices[0].price
            else:
                no_price = True
        if no_price:
            if none_equals_zero:
                return Decimal(0.0)
            else:
                return None

    def get_quote_boerse_frankfurt(self, symbol):
        # print(symbol)
        base_url = 'http://www.boerse-frankfurt.de/en/search/result?order_by=wm_vbfw.name&name_isin_wkn='
        # print(base_url+symbol)
        request = urllib.request.Request(base_url + symbol)
        try:
            response = urllib.request.urlopen(request)
        except:
            print('No connection to the internet avaliable')
            return None
        content = response.read().decode('utf-8')
        # content = urllib.request.urlopen(base_url + symbol).read().decode('UTF-8')  # .replace('\n','')
        # import pdb; pdb.set_trace()

        m = re.search('Last Price.{1,100}<span.{1,45}security-price.{1,55}>([0-9\.]{3,9})<\/', content, re.DOTALL)
        if m:
            quote = Decimal(m.group(1))
        else:
            m1 = re.search('The search for .{5,25}; delivered no results', content, re.DOTALL)
            m2 = re.search('<td class="column-bid .*?>.*?\-.*?<\/td>', content, re.DOTALL)
            if m1:
                print('No results found for', symbol)
            elif m2:
                print('No quotes accessible for', symbol)
            else:

                print('Other unknown error while retrieving the quote')
                with open(self.base_path + '/' + symbol + '.html', 'w') as myfile:
                    myfile.write(content)

            quote = None
        return quote

    def update(self, sec, date, price):
        Price.objects.get_or_create(stock_id=sec, date=date, price=price)

    def import_boerse_frankfurt(self):
        print('Start update')
        today = datetime.date.today()
        if today.weekday() >= 5:
            today = today + datetime.timedelta(days=4 - today.weekday())
        # yesterday = today + datetime.timedelta(days=-1)
        for sec in Security.objects.all():
            if not sec.isin_id.startswith('unknown'):
                # import pdb; pdb.set_trace()
                tmp_p = self.get_prices(sec, order_by_date=True)
                if tmp_p:
                    old_price_date = tmp_p[0].date
                else:
                    old_price_date = None
                if old_price_date != today:
                    quote = self.get_quote_boerse_frankfurt(sec.isin_id)
                    print('.')
                    if not quote:
                        print('x')
                    else:
                        self.update(sec, today, quote)
                else:
                    print('t')
            else:
                print('No ISIN', sec.name)
        print('Update finished')

    def import_historic_quotes(self, years=15):
        result = []
        today = datetime.date.today()
        first_day = datetime.date.today() - datetime.timedelta(days=int(years * 365))
        today_str = today.strftime('%Y-%m-%d')
        first_day_str = first_day.strftime('%Y-%m-%d')
        logger.info('Start import of historic quotes')
        for sec in Security.objects.all():
            logger.debug('Security ' + str(sec))
            no_quote = False
            no_yahoo_id = False
            if sec.yahoo_id != '' and not sec.yahoo_id.startswith('unknown'):

                try:
                    quote = ystockquote.get_historical_prices(sec.yahoo_id, first_day_str, today_str)
                except urllib.error.HTTPError:
                    no_quote = True
                else:
                    logger.debug('Found quotes')
                    for key in quote:
                        logger.debug('Security ' + str(sec))
                        self.add(sec, key, quote[key]['Close'])
            else:
                no_yahoo_id = True
            result.append({'stock_id': sec.id,
                           'yahoo_id': sec.yahoo_id,
                           'name': sec.name,
                           'no_quote': no_quote,
                           'no_yahoo_id': no_yahoo_id})
        return result

    def add(self, stock_id, date, price):
        logger.debug('Adding new price ' + str(stock_id) + ', date ' + str(date) + ', ' + str(price))
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if isinstance(price, str):
            price = Decimal(price)
        # print(type(stock_id), type(date), type(price))
        return Price.objects.get_or_create(stock_id=stock_id, date=date, price=price)


class SecuritySplit(models.Model):
    stock_id = models.ForeignKey(Security)
    date = models.DateField('date of split')
    # Splitratio 7.0 --> 1 old stock for 7 new ones
    ratio = models.DecimalField(max_digits=20, decimal_places=4)

    def get_splits_before_date(self, stock_id, before_date):
        return SecuritySplit.objects.filter(stock_id=stock_id, date__lte=before_date)

    def get_splits(self, stock_id):
        return SecuritySplit.objects.filter(stock_id=stock_id)

    def get_ratio_before_date(self, stock_id, before_date):
        splits = self.get_splits_before_date(stock_id, before_date)
        ratio = Decimal(1)
        for split in splits:
            ratio = ratio * split.ratio
        return ratio

    def add(self, stock_id, date, ratio):
        return SecuritySplit.objects.get_or_create(stock_id=stock_id, date=date, ratio=ratio)

    # def find_split_date(self, stock_id):
    #     prices = self.get_prices(stock_id)
    #     old_price = None
    #     last_unsplit_date = None
    #     suggested_ratio = None
    #     for date in reversed(sorted(prices)):
    #         new_price = prices[date]
    #         if old_price != None:
    #             if new_price / float(old_price) > 1.5:
    #                 last_unsplit_date = date
    #                 suggested_ratio = int(round(new_price / float(old_price), 0))
    #                 break
    #         old_price = new_price
    #     return last_unsplit_date, suggested_ratio


