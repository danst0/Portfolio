# Create your models here.
import datetime
from transactions.models import Transaction
from securities.models import Security, Price
from money.models import Money
from decimal import Decimal
from dateutil.relativedelta import relativedelta


class UI:
    def __init__(self):
        self.transaction = Transaction()
        self.prices = Price()
        self.secs = Security()
        self.money = Money()

    def rolling_profitability(self, from_date, to_date, user, portfolio='All'):
        time_span = (to_date - from_date).days
        no_of_month = int(time_span/30/12)
        # print(no_of_month)
        dates = []
        roi_list = []

        loop_to_date = to_date

        while loop_to_date >= from_date:

            loop_from_date = loop_to_date - relativedelta(months=12)

            print(loop_from_date, loop_to_date)

            # result = self.transaction.list_pf(portfolio, loop_from_date, loop_to_date, user)
            roi = self.transaction.get_roi(loop_from_date, loop_to_date, user, portfolio)
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
        # import pdb; pdb.set_trace()
        time_intervall = int((to_date - from_date).days/12/15)*15
        total_dividend = self.transaction.get_total_dividend(portfolio, from_date, to_date)
        # Iteration over 12 time intervals
        for i in range(12):
            loop_date = (datetime.date.today() - datetime.timedelta(days=1 + i * time_intervall))
            # import pdb; pdb.set_trace()
            stocks_at_date = self.transaction.get_total_for_portfolio(portfolio, loop_date, user)

            portfolio_value_at_date = Decimal(0)
            stocks = []
            for stock_id in stocks_at_date.keys():
                price = self.prices.get_last_price_from_stock_id(stock_id, loop_date,
                                                                 none_equals_zero=True,
                                                                 none_equals_oldest_available=True)
                if price == 0:
                    print(stock_id, 'price 0', loop_date)
                portfolio_value_at_date += stocks_at_date[stock_id]['nominal'] * price
                stocks.append((stock_id, stocks_at_date[stock_id]['nominal'], price))

            invest = self.transaction.get_total_invest(portfolio, loop_date, to_date)
            divest = self.transaction.get_total_divest(portfolio, loop_date, to_date)
            dividend_before = self.transaction.get_total_dividend(portfolio, from_date, loop_date)

            dates.append(loop_date)
            cash_values.append(self.money.get_wealth(loop_date, user))
            pf_details.append(stocks)
            # Logic of tmp_value: PF Value: reduce invests that happend after that date; further reduce by all dividends that will happen until end of horizon (vs. what already came)
            tmp_value = portfolio_value_at_date - invest + divest - (total_dividend - dividend_before)
            pf_value.append(tmp_value)

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
                            self.transaction.get_invest_divest(portfolio, cur_key, dates[interval_factor], dates[0])
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
                            self.transaction.get_invest_divest(portfolio, cur_key, dates[interval_factor], dates[0])
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
        roi = self.transaction.get_roi(from_date, to_date, user)
        if roi != 'n/a':
            roi = int(roi*100)
        return dates, pf_value, cash_values, roi

