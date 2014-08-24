# Create your models here.
from Securities.models import Security
from Transactions.models import Transaction


class UI:
    def rolling_profitability(self):
        
        dates = []
        roi_list = []
        for i in range(int(time_span / 30)):
            loop_to_date = (datetime.date.today() - datetime.timedelta(days=1 + i * 30))
            loop_from_date = (datetime.date.today() - datetime.timedelta(days=time_span + i * 30))
            stocks_at_start = self.transaction.get_portfolio('All', loop_from_date.strftime("%Y-%m-%d"))
            portfolio_value_at_start = 0.0
            for key in stocks_at_start.keys():
                portfolio_value_at_start += stocks_at_start[key] * self.prices.get_last_price_from_stock_id(key,
                                                                                                            loop_from_date.strftime(
                                                                                                                "%Y-%m-%d"),
                                                                                                            none_equals_zero=True)
            stocks_at_end = self.transaction.get_portfolio('All', loop_to_date.strftime("%Y-%m-%d"))
            portfolio_value_at_end = 0.0
            for key in stocks_at_end.keys():
                portfolio_value_at_end += stocks_at_end[key] * self.prices.get_last_price_from_stock_id(key,
                                                                                                        loop_to_date.strftime(
                                                                                                            "%Y-%m-%d"),
                                                                                                        none_equals_zero=True)

            invest = self.transaction.get_total_invest('All', loop_from_date, loop_to_date)
            divest = self.transaction.get_total_divest('All', loop_from_date, loop_to_date)
            dividend = self.transaction.get_total_dividend('All', loop_from_date, loop_to_date)

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
        plt.show()





