from django.shortcuts import render
from settings.forms import SettingsForm
from django.contrib.auth.decorators import login_required
from settings.models import Settings

# Create your views here.

@login_required
def show_settings(request):
    # if this is a POST request we need to process the form data
    try:
        existing_settings = Settings.objects.get(user=request.user)
    except:
        existing_settings = None
    form = SettingsForm(instance=existing_settings)
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:

        # details_form = DetailsForm(instance = existing_detail)
        form = SettingsForm(request.POST, instance=existing_settings)
        # check whether it's valid:
        if form.is_valid():
            instance = form.save()
            instance.user = request.user
            instance.save()
            return render(request, 'settings.html', {'block_title': 'Settings',
                                                     'form': form,
                                                     'tax_rate': form.cleaned_data['tax_rate'],
                                                     'view_update_interval': form.cleaned_data['view_update_interval'],
                                                     'expected_interest': form.cleaned_data['expected_interest'],
                                                     'active_nav': '#nav_settings',
                                                     'username': request.user.username,})
    # if a GET (or any other method) we'll create a blank form

    return render(request, 'settings.html', {'block_title': 'Settings',
                                             'form': form,
                                             'active_nav': '#nav_settings',
                                             'username': request.user.username,})