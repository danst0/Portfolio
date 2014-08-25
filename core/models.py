# Create your models here.
import datetime
from Transactions.models import Transaction
from Securities.models import Price
from decimal import Decimal
import matplotlib.pyplot as plt

class UI:
    def __init__(self):
        self.transaction = Transaction()
        self.prices = Price()
    def rolling_profitability(self, portfolio, from_date, to_date):
        time_span = 360
        dates = []
        roi_list = []
        for i in range(int(time_span / 30)):
            loop_to_date = (datetime.date.today() - datetime.timedelta(days=1 + i * 30))
            loop_from_date = (datetime.date.today() - datetime.timedelta(days=time_span + i * 30))
            stocks_at_start = self.transaction.get_stocks_in_portfolio(portfolio, loop_from_date.strftime("%Y-%m-%d"))
            portfolio_value_at_start = Decimal(0.0)
            for key in stocks_at_start.keys():
                portfolio_value_at_start += stocks_at_start[key] * self.prices.get_last_price_from_stock_id(key,
                                                                                                            loop_from_date.strftime(
                                                                                                                "%Y-%m-%d"),
                                                                                                            none_equals_zero=True)
            stocks_at_end = self.transaction.get_stocks_in_portfolio(portfolio, loop_to_date.strftime("%Y-%m-%d"))
            portfolio_value_at_end = Decimal(0.0)
            for key in stocks_at_end.keys():
                portfolio_value_at_end += stocks_at_end[key] * self.prices.get_last_price_from_stock_id(key,
                                                                                                        loop_to_date.strftime(
                                                                                                            "%Y-%m-%d"),
                                                                                                        none_equals_zero=True)

            invest = self.transaction.get_total_invest(portfolio, loop_from_date, loop_to_date)
            divest = self.transaction.get_total_divest(portfolio, loop_from_date, loop_to_date)
            dividend = self.transaction.get_total_dividend(portfolio, loop_from_date, loop_to_date)
            print(portfolio_value_at_end, invest, divest, portfolio_value_at_start, dividend)
            profit_incl_on_books = portfolio_value_at_end + invest - divest - portfolio_value_at_start + dividend
            if portfolio_value_at_start - invest != 0:
                tmp = 100 * profit_incl_on_books / (portfolio_value_at_start - invest)
            else:
                tmp = 0.0
            dates.append(loop_to_date)
            roi_list.append(tmp)
            # print('Date', loop_to_date, 'ROI', tmp)
        plt.plot(dates, roi_list, 'r')
        # plt.axis(dates)
        plt.title('Rolling Return-on-Investment; range: ' + from_date.strftime('%Y-%m-%d') + ' -- ' + to_date.strftime(
            '%Y-%m-%d'))
        plt.xlabel('%')
        plt.xticks(rotation=15)
        plt.xlabel('Date')
        plt.savefig('rolling_profitability.png')





