from django import forms
import datetime
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


class PortfolioFormStockTwoDates(forms.Form):
    time_span = 365
    security = forms.CharField(label='Security', max_length=100, initial='Apple Inc.')
    tmp_default_from = (datetime.date.today() - datetime.timedelta(days=time_span)).strftime('%Y-%m-%d')
    tmp_default_to = (datetime.date.today() - datetime.timedelta(days=0)).strftime('%Y-%m-%d')
    from_date = forms.DateField(label='Start date', initial=tmp_default_from)
    to_date = forms.DateField(label='End date', initial=tmp_default_to)
