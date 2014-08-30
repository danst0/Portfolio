from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from core.forms import PortfolioFormOneDate, PortfolioFormTwoDates
from core.models import UI
from transactions.models import Transaction

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from matplotlib.ticker import ScalarFormatter

import datetime
import random
from django.http import HttpResponse

from securities.models import Price
# Create your views here.



def index(request):
    return render(request, 'index.html')


def import_historic_quotes(request):
    # import pdb; pdb.set_trace()
    p = Price()
    result = p.import_historic_quotes()
    return render(request, 'import_historic_quotes.html', {'block_title': 'Import Historic Quotes', 'import_results': result})

def rolling_profitability_png(request, portfolio, from_date, to_date):
    fig=Figure()
    ax=fig.add_subplot(111)
    ui = UI()
    dates, roi_list = ui.rolling_profitability(portfolio,
                                               datetime.datetime.strptime(from_date, '%Y-%m-%d'),
                                               datetime.datetime.strptime(to_date, '%Y-%m-%d'))
    ax.plot_date(dates, roi_list, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def rolling_profitability(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PortfolioFormTwoDates(request.POST)
        # check whether it's valid:
        if form.is_valid():
            content = 'You are great <a href="http://google.com">so great</a>'
            return render(request, 'rolling_profitability.html', {'block_title': 'Rolling Profitability',
                                                                  'form': form,
                                                                  'content': content,
                                                                  'portfolio': form.cleaned_data['portfolio'],
                                                                  'from_date': form.cleaned_data['from_date'].strftime('%Y-%m-%d'),
                                                                  'to_date': form.cleaned_data['to_date'].strftime('%Y-%m-%d')})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PortfolioFormTwoDates()

    return render(request, 'rolling_profitability.html', {'block_title': 'Rolling Profitability',
                                                          'form': form})

def portfolio_development_png(request, portfolio, from_date, to_date):
    fig=Figure()
    ax=fig.add_subplot(111)
    ui = UI()
    dates, pf_values = ui.portfolio_development(portfolio,
                                               datetime.datetime.strptime(from_date, '%Y-%m-%d'),
                                               datetime.datetime.strptime(to_date, '%Y-%m-%d'))
    ax.plot_date(dates, pf_values, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def portfolio_development(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PortfolioFormTwoDates(request.POST)
        # check whether it's valid:
        if form.is_valid():
            return render(request, 'portfolio_development.html', {'block_title': 'Portfolio Development',
                                                                  'form': form,
                                                                  'portfolio': form.cleaned_data['portfolio'],
                                                                  'from_date': form.cleaned_data['from_date'].strftime('%Y-%m-%d'),
                                                                  'to_date': form.cleaned_data['to_date'].strftime('%Y-%m-%d')})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PortfolioFormTwoDates()

    return render(request, 'portfolio_development.html', {'block_title': 'Portfolio Development',
                                                          'form': form})

def portfolio_overview(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PortfolioFormOneDate(request.POST)
        # check whether it's valid:
        if form.is_valid():
            t = Transaction()
            content = t.list_pf(form.cleaned_data['portfolio'], form.cleaned_data['from_date'].strftime('%Y-%m-%d'))
            return render(request, 'portfolio_overview.html', {'block_title': 'Portfolio Overview',
                                                               'form': form,
                                                               'portfolio': form.cleaned_data['portfolio'],
                                                               'from_date': form.cleaned_data['from_date'].strftime('%Y-%m-%d'),
                                                               'content': content})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PortfolioFormOneDate()

    return render(request, 'portfolio_overview.html', {'block_title': 'Portfolio Overview',
                                                       'form': form})

    self.portfolio.print_pf(my_date)