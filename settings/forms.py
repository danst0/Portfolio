from django import forms
import datetime
# Forms

class SettingsForm(forms.Form):
    expected_interest = forms.DecimalField(label='Expected interest rate (%)', initial='8.8')
    tax_rate = forms.DecimalField(label='Tax rate (%)', initial='26.4')
    inflation = forms.DecimalField(label='Long term inflation rate (%)', initial='2.5')
