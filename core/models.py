# Create your models here.
import datetime
from Transactions.models import Transaction
from Securities.models import Price
from decimal import Decimal


class UI:
    def __init__(self):
        self.transaction = Transaction()
        self.prices = Price()
    def rolling_profitability(self, portfolio, from_date, to_date):
        time_span = (to_date - from_date).days
        interval = int(time_span / 12)
        dates = []
        roi_list = []
        for i in range(int(time_span / interval)):
            loop_to_date = (to_date - datetime.timedelta(days=1 + i * 30))
            loop_from_date = (to_date - datetime.timedelta(days=time_span + i * 30))
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
        return dates, roi_list





