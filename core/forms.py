from django import forms
# Forms

class RollingProfitabilityForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)