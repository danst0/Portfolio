from django import forms
import datetime
from dateutil import rrule, relativedelta
from settings.models import Settings


def adjust_dates(update_interval, to_date, from_date):
    # print(from_date, to_date, to_date.weekday())
    # print(update_interval)
    # import pdb;pdb.set_trace()
    if update_interval == 'quarterly':
        month_delta = to_date.month % 3
        # we do have a quarter month and we are already on the last day
        if month_delta == 0 and to_date == to_date + relativedelta.relativedelta(day=31):
            new_to_date = to_date
        elif month_delta == 0:
            new_to_date = to_date + relativedelta.relativedelta(months=-3)
            new_to_date += relativedelta.relativedelta(day=31)
        # in any month: go back three month, go forward number of mod month
        else:
            new_to_date = to_date + relativedelta.relativedelta(months=-month_delta)
            new_to_date += relativedelta.relativedelta(day=31)

    elif update_interval == 'monthly':
        new_to_date = to_date + relativedelta.relativedelta(days=+1, months=-1)
        new_to_date += relativedelta.relativedelta(day=31)

    elif update_interval == 'weekly':
        new_to_date = to_date + relativedelta.relativedelta(weekday=relativedelta.SU(-1))
    elif update_interval == 'instant':
        new_to_date = to_date
    delta = (to_date - from_date).days
    # print('delta', delta)
    if delta != 0:
        from_date = new_to_date + relativedelta.relativedelta(days=-delta)
    else:
        from_date = new_to_date + relativedelta.relativedelta(years=-1)
    to_date = new_to_date
    # print(from_date, to_date, to_date.weekday())
    return to_date, from_date



# Forms

class PortfolioFormOneDate(forms.Form):

    #portfolio = forms.CharField(label='Portfolio', max_length=100, initial='All')
    time_span = 365
    tmp_default_to = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y-%m-%d')
    from_date = forms.DateField(label='Date', initial=tmp_default_to)


class PortfolioFormTwoDates(forms.Form):
    #portfolio = forms.CharField(label='Portfolio', max_length=100, initial='All')
    time_span = 365
    tmp_default_from = (datetime.date.today() - datetime.timedelta(days=time_span)).strftime('%Y-%m-%d')
    tmp_default_to = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y-%m-%d')
    from_date = forms.DateField(label='Start date', initial=tmp_default_from)
    to_date = forms.DateField(label='End date', initial=tmp_default_to)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.delta = None
        super(PortfolioFormTwoDates, self).__init__(*args, **kwargs)

    def clean(self):
        my_cleaned_data = self.cleaned_data
        update_interval = Settings().get_setting(self.user, 'view_update_interval')
        # update_interval = 'quarterly'
        to_date = my_cleaned_data['to_date']
        from_date = my_cleaned_data['to_date']
        to_date, from_date = adjust_dates(update_interval, to_date, from_date)
        # print(type(to_date))
        # print(type(from_date))
        form_data = self.data.copy()
        form_data['to_date'] = to_date.strftime('%Y-%m-%d')
        form_data['from_date'] = from_date
        self.data = form_data
        my_cleaned_data['to_date'] = to_date
        my_cleaned_data['from_date'] = from_date
        return my_cleaned_data


class PortfolioFormStockTwoDates(forms.Form):
    time_span = 365
    security = forms.CharField(label='Security', max_length=100, initial='Apple Inc.')
    tmp_default_from = (datetime.date.today() - datetime.timedelta(days=time_span)).strftime('%Y-%m-%d')
    tmp_default_to = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y-%m-%d')
    from_date = forms.DateField(label='Start date', initial=tmp_default_from)
    to_date = forms.DateField(label='End date', initial=tmp_default_to)
