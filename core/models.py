# Create your models here.
import datetime
from transactions.models import Transaction
from securities.models import Security, Price
from money.models import Money
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from functools import lru_cache
import logging
logger = logging.getLogger(__name__)

class UI:
    def __init__(self):
        self.transaction = Transaction()
        self.prices = Price()
        self.secs = Security()
        self.money = Money()
    def recommendation(self, user):
        from_date = datetime.date.today() - datetime.timedelta(days=2*360)
        to_date = datetime.date.today()

        result = self.transaction.list_pf(from_date, to_date, user)
        result = sorted(result, key=lambda x: float(x['roi'][:-1]))
        # get a reasonable number of results, betwenn 3 and five, depending on number of positions
        number_of_results = max(min(int(len(result)/10), 5), 3)
        # remove that are > 20%-points from total roi
        total_roi = self.transaction.get_total_roi(from_date, to_date, user)

        worst_five = result[:number_of_results]
        best_five = result[-number_of_results:]
        # print(worst_five)
        # print(best_five)
        return best_five, worst_five

    def rolling_profitability(self, from_date, to_date, user, portfolio='All'):
        time_span = (to_date - from_date).days
        no_of_month = int(time_span/30/12)
        # print(no_of_month)
        dates = []
        roi_list = []

        loop_to_date = to_date

        while loop_to_date >= from_date:

            loop_from_date = loop_to_date - relativedelta(months=12)

            # print(loop_from_date, loop_to_date)

            # result = self.transaction.list_pf(portfolio, loop_from_date, loop_to_date, user)
            roi = self.transaction.get_total_roi(loop_from_date, loop_to_date, user, portfolio)
            # print(hash(self))

            if roi != 'n/a':
                roi = int(roi *100)
            else:
                roi = 0

            dates.append(loop_to_date)
            # print(roi, tmp)
            roi_list.append(roi)

            loop_to_date = loop_to_date - relativedelta(months=no_of_month)
        dates = reversed(dates)
        roi_list = reversed(roi_list)
        return dates, roi_list

    def portfolio_development(self, from_date, to_date, user, portfolio='All'):
        dates = []
        pf_details = []
        cash_values = []
        pf_value = []
        invest_values = []
        divest_values = []
        dividend_values = []
        # import pdb; pdb.set_trace()
        time_intervall = int((to_date - from_date).days/12/15)*15
        total_dividend = self.transaction.get_total_dividend(user, from_date, to_date, portfolio=portfolio)
        # Iteration over 12 time intervals
        t1 = datetime.datetime.now()
        for i in range(12):

            loop_date = (to_date - datetime.timedelta(days=i * time_intervall))
            last_loop_date = (to_date - datetime.timedelta(days=(i+1) * time_intervall))
            # import pdb; pdb.set_trace()

            stocks_at_date = self.transaction.get_total_for_portfolio(portfolio, loop_date, user)

            portfolio_value_at_date = Decimal(0)
            stocks = []

            for stock_id in stocks_at_date.keys():
                price = self.prices.get_last_price_from_stock_id(stock_id, loop_date,
                                                                 none_equals_zero=True,
                                                                 none_equals_oldest_available=True)

                # print(self.prices.get_last_price_from_stock_id.cache_info())
                if price == 0:
                    print(stock_id, 'price 0', loop_date)
                portfolio_value_at_date += stocks_at_date[stock_id]['nominal'] * price
                stocks.append((stock_id, stocks_at_date[stock_id]['nominal'], price))

            invest = self.transaction.get_total_invest(user, loop_date, to_date, portfolio)
            divest = self.transaction.get_total_divest(user, loop_date, to_date, portfolio)
            dividend_before = self.transaction.get_total_dividend(user, from_date, loop_date, portfolio=portfolio)

            invest_values.append(-self.transaction.get_total_invest(user, last_loop_date, loop_date))
            divest_values.append(self.transaction.get_total_divest(user, last_loop_date, loop_date))
            dividend_values.append(self.transaction.get_total_dividend(user, last_loop_date, loop_date))

            dates.append(loop_date)
            cash_values.append(self.money.get_wealth(loop_date, user))

            pf_details.append(stocks)
            # Logic of tmp_value: PF Value: reduce invests that happend after that date; further reduce by all dividends that will happen until end of horizon (vs. what already came)
            tmp_value = portfolio_value_at_date - invest + divest - (total_dividend - dividend_before)
            pf_value.append(tmp_value)

        income_dates, incomes, expenses = self.money.calc_average(user, from_date, to_date, full_set=True)
        logger.debug('time ' + str(datetime.datetime.now() - t1))
        # print(__name__)

        # print(income_dates)
        # Drivers vs. 1 intervall earlier
        # print('Now', dates[0])
        # print('-1 int', dates[1])
        delta_keys = []
        interval_factor = 2
        for stock in pf_details[0]:
            cur_key = stock[0]
            cur_nom = stock[1]
            cur_price = stock[2]
            for old_stock in pf_details[interval_factor]:
                if cur_key == old_stock[0]:
                    # print(cur_key,
                    #       'Invest', self.transaction.get_invest_divest('All', cur_key, dates[interval_factor], dates[0]))
                    # print('Delta in value', cur_nom * cur_price - old_stock[1] * old_stock[2],
                    #       'Old value', old_stock[1] * old_stock[2],
                    #       'New value', cur_nom * cur_price,
                    #       'Nom', old_stock[1], cur_nom,
                    #       'EUR', old_stock[2],  cur_price)
                    delta = cur_nom * cur_price - old_stock[1] * old_stock[2] +\
                            self.transaction.get_invest_divest(user, cur_key, dates[interval_factor], dates[0], portfolio)
                    delta_keys.append([cur_key, delta])
        delta_keys = sorted(delta_keys, key=lambda x: abs(x[1]), reverse=True)
        print('Total deviation vs. ' + str(interval_factor*time_intervall) + ' days ago:', pf_value[0] - pf_value[interval_factor], '; major drivers:')
        if delta_keys:
            for i in range(5):
                print(i + 1, ': ' + str(delta_keys[i][0]), '(', str(delta_keys[i][1]), ')')

        # Drivers vs. 2 intervall earlier
        delta_keys = []
        interval_factor = 4
        for stock in pf_details[0]:
            cur_key = stock[0]
            cur_nom = stock[1]
            cur_price = stock[2]
            for old_stock in pf_details[interval_factor]:
                if cur_key == old_stock[0]:
                    # print(cur_key,
                    #       'Invest', self.transaction.get_invest_divest('All', cur_key, dates[interval_factor], dates[0]))
                    # print('Delta in value', cur_nom * cur_price - old_stock[1] * old_stock[2],
                    #       'Old value', old_stock[1] * old_stock[2],
                    #       'New value', cur_nom * cur_price,
                    #       'Nom', old_stock[1], cur_nom,
                    #       'EUR', old_stock[2],  cur_price)
                    delta = cur_nom * cur_price - old_stock[1] * old_stock[2] +\
                            self.transaction.get_invest_divest(user, cur_key, dates[interval_factor], dates[0], portfolio)
                    delta_keys.append([cur_key, delta])
        # print(delta_keys)
        delta_keys = sorted(delta_keys, key=lambda x: abs(x[1]), reverse=True)
        print('Total deviation vs. ' + str(interval_factor * time_intervall) + ' days ago:', pf_value[0] - pf_value[interval_factor], '; major drivers:')
        if delta_keys:
            for i in range(5):
                print(i + 1, ': ' + str(delta_keys[i][0]), '(', str(delta_keys[i][1]),')')

        dates = reversed(dates)
        pf_value = reversed(pf_value)
        cash_values = reversed(cash_values)
        invest_values = reversed(invest_values)
        divest_values = reversed(divest_values)
        dividend_values = reversed(dividend_values)

        roi = self.transaction.get_total_roi(from_date, to_date, user)
        if roi != 'n/a':
            roi = int(roi*100)
        return dates, pf_value, cash_values,\
               {'dates': income_dates, 'income': incomes, 'expense': expenses},\
               {'invest': invest_values, 'divest': divest_values, 'dividend': dividend_values},\
               roi

