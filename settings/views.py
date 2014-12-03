from django.shortcuts import render
from settings.forms import SettingsForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def show_settings(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SettingsForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            return render(request, 'settings.html', {'block_title': 'Settings',

                                                               'form': form,
                                                               'tax_rate': form.cleaned_data['from_date'],
                                                               'expected_interest': form.cleaned_data['to_date'],

                                                               'username': request.user.username,})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = SettingsForm()

    return render(request, 'settings.html', {'block_title': 'Settings',
                                                       'form': form,
                                                       'username': request.user.username,})