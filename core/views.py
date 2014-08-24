from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from core.forms import RollingProfitabilityForm


# Create your views here.



def index(request):
    return render(request, 'index.html')


def update(request):
    #return HttpResponse("Hello, world. You're at the m2/update index.")
    return render(request, 'update.html')


def rolling_profitability(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RollingProfitabilityForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print('clean', form.cleaned_data)
            return render(request, 'rolling_profitability.html', {'form': form})
            #return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = RollingProfitabilityForm()

    return render(request, 'rolling_profitability.html', {'form': form})