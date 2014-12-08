from django import forms
import datetime
from settings.models import Settings

# Forms



class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['expected_interest', 'tax_rate', 'inflation', 'view_update_interval']
    # expected_interest = forms.DecimalField(label='Expected interest rate (%)', initial='8.8')
    # tax_rate = forms.DecimalField(label='Tax rate (%)', initial='26.4')
    # inflation = forms.DecimalField(label='Long term inflation rate (%)', initial='2.5')
    # view_interval = forms.ChoiceField(label='Interval for stock update', choices=models.Settings.options)