from django import forms
import datetime
# Forms

class RollingProfitabilityForm(forms.Form):
    portfolio = forms.CharField(label='Portfolio', max_length=100, initial='All')
    time_span = 360
    tmp_default = (datetime.date.today() - datetime.timedelta(days=time_span)).strftime('%Y-%m-%d')
    from_date = forms.DateField(label='Start date', initial=tmp_default)
    #from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
    tmp_default = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    to_date = forms.DateField(label='End date', initial=tmp_default)
    #to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()