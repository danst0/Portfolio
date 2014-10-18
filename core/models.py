# Create your models here.
import datetime
from transactions.models import Transaction
from securities.models import Security, Price
from decimal import Decimal


class UI:
    def __init__(self):
        self.transaction = Transaction()
        self.prices = Price()
        self.secs = Security()

    def rolling_profitability(self, portfolio, from_date, to_date):
        time_span = (to_date - from_date).days
        interval = int(time_span / 12)
        dates = []
        roi_list = []

        for i in range(int(time_span / interval)):
            loop_to_date = (to_date - datetime.timedelta(days=i * 30))
            loop_from_date = (to_date - datetime.timedelta(days=interval + i * interval))
            stocks_at_start = self.transaction.get_total_for_portfolio(portfolio, loop_from_date)
            # print(stocks_at_start)


            portfolio_value_at_start = Decimal(0.0)
            for key in stocks_at_start.keys():
                # print(key)
                # print(self.prices.get_last_price_from_stock_id(key,
                #                                                                      loop_from_date,
                #                                                                      none_equals_zero=True))
                # print(stocks_at_start[key]['nominal'])
                # import pdb; pdb.set_trace()
                portfolio_value_at_start += stocks_at_start[key]['nominal'] *\
                                            self.prices.get_last_price_from_stock_id(key,
                                                                                     loop_from_date,
                                                                                     none_equals_zero=True)
                # print(self.prices.get_last_price_from_stock_id(key, loop_from_date, none_equals_zero=True))
            stocks_at_end = self.transaction.get_total_for_portfolio(portfolio, loop_to_date)
            portfolio_value_at_end = Decimal(0.0)
            for key in stocks_at_end.keys():
                portfolio_value_at_end += stocks_at_end[key]['nominal'] * self.prices.get_last_price_from_stock_id(key,
                                                                                                                   loop_to_date,
                                                                                                                   none_equals_zero=True)

            # import pdb; pdb.set_trace()
            invest = self.transaction.get_total_invest(portfolio, loop_from_date, loop_to_date)
            divest = self.transaction.get_total_divest(portfolio, loop_from_date, loop_to_date)
            dividend = self.transaction.get_total_dividend(portfolio, loop_from_date, loop_to_date)
            print('end', portfolio_value_at_end, 'inv', invest, 'dive', divest, 'start', portfolio_value_at_start, 'div', dividend)
            profit_incl_on_books = portfolio_value_at_end + invest - divest - portfolio_value_at_start + dividend
            print('profit', profit_incl_on_books)
            if portfolio_value_at_start - invest != 0:
                tmp = 100 * profit_incl_on_books / (portfolio_value_at_start - invest)
            else:
                tmp = 0.0
            dates.append(loop_to_date)
            roi_list.append(tmp)
        return dates, roi_list


    def portfolio_development(self, portfolio, from_date, to_date):
        dates = []
        pf_details = []
        pf_value = []
        # import pdb; pdb.set_trace()
        time_intervall = int((to_date - from_date).days/12/15)*15
        total_dividend = self.transaction.get_total_dividend('All', from_date, to_date)
        for i in range(12):
            loop_date = (datetime.date.today() - datetime.timedelta(days=1 + i * time_intervall))
            stocks_at_date = self.transaction.get_total_for_portfolio('All', loop_date.strftime("%Y-%m-%d"))
            portfolio_value_at_date = Decimal(0)
            stocks = []
            for stock_id in stocks_at_date.keys():
                price = self.prices.get_last_price_from_stock_id(stock_id, loop_date.strftime("%Y-%m-%d"),
                                                                 none_equals_zero=True)
                portfolio_value_at_date += stocks_at_date[stock_id]['nominal'] * price
                stocks.append((stock_id, stocks_at_date[stock_id]['nominal'], price))

            invest = self.transaction.get_total_invest('All', loop_date, to_date)
            divest = self.transaction.get_total_divest('All', loop_date, to_date)
            dividend_before = self.transaction.get_total_dividend('All', from_date, loop_date)

            dates.append(loop_date)
            pf_details.append(stocks)
            # Logic of tmp_value: PF Value: reduce invests that happend after that date; further reduce by all dividends that will happen until end of horizon (vs. what already came)
            tmp_value = portfolio_value_at_date - invest + divest - (total_dividend - dividend_before)
            pf_value.append(tmp_value)

        # Drivers vs. 1 intervall earlier
        delta_keys = []
        for stock in pf_details[0]:
            cur_key = stock[0]
            cur_nom = stock[1]
            cur_price = stock[2]
            for old_stock in pf_details[1]:
                if cur_key == old_stock[0]:
                    # print(cur_nom * cur_price - old_stock[1] * old_stock[2], old_stock[1] * old_stock[2], cur_nom * cur_price, 'Nom', old_stock[1], cur_nom, 'EUR', old_stock[2],  cur_price)
                    #					print(cur_key, '::', self.transaction.get_invest_divest('All', cur_key, dates[1], dates[0]))
                    delta = cur_nom * cur_price - old_stock[1] * old_stock[2] + self.transaction.get_invest_divest(
                        'All', cur_key, dates[1], dates[0])
                    delta_keys.append([cur_key, delta, abs(delta)])
        delta_keys = sorted(delta_keys, key=lambda x: x[2], reverse=True)
        print('Total deviation vs. ' + str(time_intervall) + ' days ago:', pf_value[0] - pf_value[1], '; major drivers:')
        for i in range(3):
            print(i + 1, ': ' + str(delta_keys[i][0]), '(', str(delta_keys[i][1]), ')')

        # Drivers vs. 2 intervall earlier
        delta_keys = []
        for stock in pf_details[0]:
            cur_key = stock[0]
            cur_nom = stock[1]
            cur_price = stock[2]
            for old_stock in pf_details[2]:
                if cur_key == old_stock[0]:
                    delta = cur_nom * cur_price - old_stock[1] * old_stock[2] + self.transaction.get_invest_divest(
                        'All', cur_key, dates[2], dates[0])
                    delta_keys.append([cur_key, delta, abs(delta)])
        # print(delta_keys)
        delta_keys = sorted(delta_keys, key=lambda x: x[2], reverse=True)
        print('Total deviation vs. ' + str(2* time_intervall) + ' days ago:', pf_value[0] - pf_value[2], '; major drivers:')
        for i in range(3):
            print(i + 1, ': ' + str(delta_keys[i][0]), '(', str(delta_keys[i][1]),')')
            # print(delta_keys)

        return dates, pf_value

