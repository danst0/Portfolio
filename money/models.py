from django.db import models
from decimal import Decimal
from transactions.models import Transaction
import statistics
import math
import os
import csv
import datetime
from django.utils import timezone
from dateutil import relativedelta
from django.contrib.auth.models import User

# Create your models here.

class Money(models.Model):
    user = models.ForeignKey(User, null=True, default=None)
    to_date = models.DateField('End date of income/expense, date of total')
    # total, income, expense; income, expense, optional with fallback = None
    income = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True, default=None)
    expense = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True, default=None)
    total_in_end = models.DecimalField(max_digits=20, decimal_places=4)

    base_path = os.path.expanduser('~') + '/Desktop/PDFs'


    def return_complete_sets(self):
        transactions = Money.objects.all().order_by('to_date')
        complete_set = {}
        # import pdb; pdb.set_trace()
        for num, trans in enumerate(transactions):
            if num != 0:
                complete_set[trans.to_date] = {}
                complete_set[trans.to_date]['total_in_beginning'] = transactions[num - 1].total_in_end
                if trans.income and not trans.expense:
                    complete_set[trans.to_date]['income'] = trans.income
                    complete_set[trans.to_date]['expense'] = -(trans.total_in_end - transactions[num - 1].total_in_end - trans.income)
                elif trans.expense and not trans.income:
                    complete_set[trans.to_date]['income'] = trans.total_in_end - transactions[num - 1].total_in_end + trans.expense
                    complete_set[trans.to_date]['expense'] = trans.expense
                elif trans.expense and trans.income:
                    complete_set[trans.to_date]['income'] = trans.income
                    complete_set[trans.to_date]['expense'] = trans.expense
                else:
                    complete_set[trans.to_date]['income'] = Decimal(0)
                    complete_set[trans.to_date]['expense'] = Decimal(0)
                complete_set[trans.to_date]['total_in_end'] = trans.total_in_end
            # else:
            #     complete_set[trans.to_date]['total_in_beginning'] = Decimal(0)
            #     complete_set[trans.to_date]['income'] = trans.total_in_end
            #     complete_set[trans.to_date]['expense'] = Decimal(0)
            #     complete_set[trans.to_date]['total_in_end'] = trans.total_in_end
        return complete_set

    def calc_average(self, from_date=None, to_date=None):
        my_set = self.return_complete_sets()
        # import pdb; pdb.set_trace()
        incomes = []
        expenses = []
        last_date = None
        t = Transaction()
        for date, value in sorted(my_set.items()):
            if last_date:
                invest = t.get_total_invest('All', last_date, date)
                divest = t.get_total_divest('All', last_date, date)
                dividend = t.get_total_dividend('All', last_date, date)
            else:
                invest, divest, dividend = 0, 0, 0
            last_date = date
            # print(10*'---')
            # print(date)
            # print('Divest', divest)
            # print('Invest', invest)
            # print('Dividend', dividend)
            # print(value['income'])
            # print(value['expense'])
            # print(value['expense']+ divest + invest + dividend)
            incomes.append(value['income'])
            expenses.append(value['expense'] + divest + invest + dividend)
        incomes = list(incomes)
        expenses = list(expenses)
        if incomes != []:
            median_income = statistics.mean(incomes)
        else:
            median_income = 0
        if expenses != []:
            median_expense = statistics.mean(expenses)
        else:
            median_expense = 0
        return median_income, median_expense

    def get_wealth(self, date, user):
        transactions = Money.objects.filter(to_date__lte=date, user=user).order_by('-to_date')
        # print(date)
        # print(transactions)
        transactions = list(transactions)
        if transactions != []:
            result = transactions[0].total_in_end
        else:
            result = Decimal(0)
        return result


    def get_current_wealth(self, user):
        today = datetime.date.today()
        result = self.get_wealth(today, user)
        return result

    def calc_wealth_next_month(self, initial_cash_value, initial_pf_value, no_of_month_to_go, income, expense, interest_p_a, development):
        delta_income_expense = income - expense
        cash_percentage = Decimal(0)
        if initial_cash_value + initial_pf_value != 0:
            cash_percentage = initial_cash_value/(initial_cash_value + initial_pf_value)

        # print(cash_percentage, no_of_month_to_go)
        no_of_month_to_go -= 1
        end_of_month_pf_value = (initial_pf_value + delta_income_expense * (1-cash_percentage)) * Decimal(math.pow(1 + interest_p_a, 1/12))
        end_of_month_cash_value = initial_cash_value + delta_income_expense * cash_percentage
        development.append(round(float(end_of_month_cash_value + end_of_month_pf_value), 2))
        if no_of_month_to_go == 0:
            # print('good return', end_of_month_cash_value + end_of_month_pf_value, development)
            return end_of_month_cash_value + end_of_month_pf_value, development
        else:
            return self.calc_wealth_next_month(end_of_month_cash_value, end_of_month_pf_value, no_of_month_to_go,
                                               income, expense, interest_p_a, development)
    def month_delta(self, date_str):
        r = relativedelta.relativedelta(datetime.datetime.now(), datetime.datetime.strptime(date_str, '%Y-%m-%d'))
        # import pdb;pdb.set_trace()
        return -(r.years * 12 + r.months)

    def simulate_pension(self, wealth, monthly_interest_rate, monthly_pension, development):
        month_counter = 0
        max_count = 1200
        while wealth > 0 and month_counter < max_count:
            # print(wealth)
            month_counter += 1
            wealth = wealth * Decimal(1+monthly_interest_rate) - monthly_pension
            development.append(round(float(wealth), 2))
        return month_counter, development

    def calc_pension(self, future_wealth, month_to_go, yearly_interest_rate, development):
        # import pdb; pdb.set_trace()
        # future_wealth = 1000
        # print(yearly_interest_rate)
        # print(future_wealth)
        # yearly_interest_rate = 0.05
        monthly_interest_rate = math.pow(yearly_interest_rate+1, 1/12)-1
        # import pdb; pdb.set_trace()
        monthly_pension = future_wealth * Decimal(monthly_interest_rate * 1.00001)

        delta_month = 99

        while abs(delta_month/month_to_go) > 0.01:
            # print(delta_month, month_to_go, delta_month/month_to_go)
            print('pension', monthly_pension)
            tmp_development = []
            no_of_month, tmp_development = self.simulate_pension(future_wealth, monthly_interest_rate, monthly_pension, tmp_development)
            delta_month = no_of_month - month_to_go
            print('delta', delta_month)
            # import pdb; pdb.set_trace()
            monthly_pension = monthly_pension * Decimal(1 + (0.00001 * delta_month))
        development += tmp_development
        # print(monthly_pension)
        # print(month_to_go, no_of_month)
        return monthly_pension, development

    def mp(self, wealth, year_of_retirement, year_of_death, interest_rate, development):
        """
        :param wealth: Starting point for wealth at retirement age
        :param year_of_retirement: when to retire
        :param year_of_death: when to die
        :param interest_rate: applicable interest rate
        :return: monthly return/pension while using up all money
        """
        if wealth != 0:
            future_delta = self.month_delta(str(year_of_death)+'-12-31') - self.month_delta(str(year_of_retirement)+'-12-31')
            monthly_pension, development = self.calc_pension(wealth, future_delta, interest_rate, development)
        else:
            monthly_pension = 0
        return monthly_pension, development

    def aggregate_results(self, user):
        t = Transaction()
        print('Start aggregating results')
        year_of_death = 2080
        current_pf_value = t.get_pf_value(timezone.now().date(), user)
        median_income, median_expense = self.calc_average(user)
        total_wealth = current_pf_value + self.get_current_wealth(user)

        timespan = 3*365
        from_date = (timezone.now() - datetime.timedelta(days=timespan)).date()
        to_date = timezone.now().date()
        # import pdb;pdb.set_trace()
        # print(from_date, to_date, timespan)
        # print(t.get_roi('All', from_date, to_date, user))
        current_interest_rate = math.pow(t.get_roi(from_date, to_date, user) + 1,
                                          Decimal(365/timespan))-1
        # Regression to mean
        # confidence for current_interest_rate as a predictor for future success
        confidence = 0.2
        # Average interest rate as more accurate predictor. Here Dow Jones performance between 1975 and 2013
        average_interest_rate = 0.088
        expected_interest_rate = (current_interest_rate - average_interest_rate) * confidence + average_interest_rate
        # Recalibrate expected interest rate for retirement time with new assumptions
        confidence = 0.1
        # Average interest rate as more accurate predictor. Here Dow Jones performance between 1975 and 2013
        average_interest_rate_retirement = 0.03
        expected_interest_rate_retirement = (current_interest_rate - average_interest_rate_retirement) * confidence + average_interest_rate_retirement
        delta_2015 = self.month_delta('2015-12-31')
        # print(delta_2015)
        wealth_in_2015, development = self.calc_wealth_next_month(self.get_current_wealth(user),
                                                                  current_pf_value,
                                                                  delta_2015,
                                                                  median_income,
                                                                  median_expense,
                                                                  expected_interest_rate, [])

        result_development = {}
        result_development['incomeexpense'] = median_income-median_expense
        result_development['interest'] = expected_interest_rate*100
        result_development['interest_retirement'] = expected_interest_rate_retirement*100
        for year_of_retirement in [2020, 2025, 2030]:
            # print(year_of_retirement)
            delta = self.month_delta(str(year_of_retirement)+'-12-31')
            wealth, development = self.calc_wealth_next_month(self.get_current_wealth(user),
                                                 current_pf_value,
                                                 delta,
                                                 median_income,
                                                 median_expense,
                                                 expected_interest_rate, [])

            # print('Wealth ok')
            # print(wealth, year_of_retirement)

            monthly_pension, development = self.mp(wealth,
                                      year_of_retirement,
                                      year_of_death,
                                      expected_interest_rate_retirement, development)
            # print('Pension ok', monthly_pension)
            short_development = []
            for num, item in enumerate(development):
                if num % (12*5) == 0:
                    short_development.append(item)

            result_development[year_of_retirement] = short_development
            result_development['wealth' + str(year_of_retirement)] = wealth
            result_development['pension' + str(year_of_retirement)] = monthly_pension
            #result.append({'text': 'Estimated wealth '+str(year_of_retirement), 'value': wealth})

            #result.append({'text': 'Retirement starting in '+str(year_of_retirement)+
            #                       ', monthly payments, when using the money until '+str(year_of_death)+
            #                       ', monthly payments:',
            #               'value': monthly_pension})
        return result_development

    def import_outbank(self, path):
        file = 'Alle Umsätze bis 2014-09-28.csv'
        if path != file:
            return []
        # Source format
        # "Buchungstext";"Währung";"Betrag";"Buchungstag";"Valuta-Datum";"Empfänger/Auftraggeber";
        # "Bankleitzahl";"Kontonummer";"Verwendungszweck";"Vormerkung";"Buchungsschlüssel";"Kommentar";
        # "Kategorie";"PayPal Empfänger/Auftraggeber";"PayPal An E-Mail";"PayPal Von E-Mail";"PayPal Gebühr";
        # "PayPal Transaktionscode";"PayPal Status"
        relevant_rows = []
        with open(self.base_path + '/' + file, encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if not row[0].startswith('Buchungstext') and row[0] != (''):
                    print(row)
                    # target format:
                    # {'type': 'd', 'name': name, 'date': date, 'nominal': Decimal(0), 'value': value,
                    #     'cost': Decimal(0), 'isin': isin}
                    # name = short_name_long_name[row[1]]
                    # date = datetime.datetime.strptime(row[0], "%d.%m.%Y").date()
                    # nominal = Decimal(make_float(row[2]))
                    # value = Decimal(make_float(row[3].replace(u'\xa0€', u'')))
                    # cost = Decimal(make_float(row[4].replace(u'\xa0€', u'')))
                    # total = Decimal(make_float(row[5].replace(u'\xa0€', u'')))
                    # if value == 0:
                    #     value = total
                    # # import pdb; pdb.set_trace()
                    # if total > 0:
                    #     type = 'b'
                    # else:
                    #     type = 'd'
                    # relevant_rows.append({'type': type,
                    #                       'date': date,
                    #                       'name': name,
                    #                       'nominal': nominal,
                    #                       'value': abs(value),
                    #                       'cost': abs(cost),
                    #                       'isin': None})
        # print(relevant_rows)
        return relevant_rows

    def __str__(self):
        return str(self.total_in_end) + '::' + str(self.to_date)