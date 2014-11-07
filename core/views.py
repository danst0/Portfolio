from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from core.forms import PortfolioFormOneDate, PortfolioFormTwoDates, PortfolioFormStockTwoDates
from core.models import UI
from securities.models import Security
from transactions.models import Transaction
from money.models import Money

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from matplotlib.ticker import ScalarFormatter

import datetime
from django.utils import timezone
from django.http import HttpResponse

from securities.models import Price
# Create your views here.



def index(request):
    return render(request, 'index.html')

def import_outbank(request):
    # import pdb; pdb.set_trace()
    m = Money()
    result = m.import_outbank()
    return render(request, 'import_outbank.html', {'block_title': 'Import Outbank', 'import_results': result})

def import_cortalconsors_quotes(request):
    p = Price()
    result = p.import_cortalconsors_quotes()
    return render(request, 'import_cortalconsors_quotes.html', {'block_title': 'Import CortalConsors Quotes', 'import_results': result})

def import_historic_quotes(request):
    # import pdb; pdb.set_trace()
    p = Price()
    result = p.import_historic_quotes()
    return render(request, 'import_historic_quotes.html', {'block_title': 'Import Historic Quotes', 'import_results': result})

def stock_graph_png(request, security, from_date, to_date):
    s = Security()
    sec = s.find(security)
    fig=Figure()
    ax=fig.add_subplot(111)

    p = Price()
    dates, values = p.get_dates_and_prices(sec, from_date, to_date)
    ax.plot_date(dates, values, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    # import pdb; pdb.set_trace()
    ax.set_ylabel(sec.name)
    ax.set_xlabel('Date')
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def stock_graph(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PortfolioFormStockTwoDates(request.POST)
        # check whether it's valid:
        if form.is_valid():
            content = 'Stock price development for shown timeframe'
            return render(request, 'stock_graph.html', {'block_title': 'Security Graph',
                                                                  'form': form,
                                                                  'content': content,
                                                                  'security': form.cleaned_data['security'],
                                                                  'from_date': form.cleaned_data['from_date'].strftime('%Y-%m-%d'),
                                                                  'to_date': form.cleaned_data['to_date'].strftime('%Y-%m-%d')})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PortfolioFormStockTwoDates()

    return render(request, 'stock_graph.html', {'block_title': 'Security Graph',
                                                          'form': form})



def rolling_profitability_png(request, portfolio, from_date, to_date):
    fig=Figure()
    ax=fig.add_subplot(111)
    ui = UI()
    dates, roi_list = ui.rolling_profitability(portfolio,
                                               datetime.datetime.strptime(from_date, '%Y-%m-%d'),
                                               datetime.datetime.strptime(to_date, '%Y-%m-%d'))
    ax.plot_date(dates, roi_list, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.set_xlabel('Date')
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
            content = 'Rolling profitability for shown timeframe'
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
    ax.set_xlabel('Date')
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def roi_cake_png(request, portfolio, from_date, to_date):
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
    ax.set_xlabel('Date')
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
def new_invest(request):
    t = Transaction()
    m = Money()
    today = timezone.now().date()
    portfolio_parts = t.get_total_per_type('All', today)
    wealth = m.get_wealth(today)
    # print(wealth)
    # print(portfolio_parts)
    content = list(portfolio_parts.items())
    content.append(('Cash', wealth))
    content = sorted(content, key=lambda x: x[0])
    # print(content)

    ##### XXXXX HIER WEITER ARBEITEN
    return render(request, 'new_invest.html', {'block_title': 'New Investments', 'content': content})

def portfolio_overview(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PortfolioFormTwoDates(request.POST)
        # check whether it's valid:
        if form.is_valid():
            t = Transaction()
            content = t.list_pf(form.cleaned_data['portfolio'],
                                form.cleaned_data['from_date'],
                                form.cleaned_data['to_date'])
            return render(request, 'portfolio_overview.html', {'block_title': 'Portfolio Overview',
                                                               'form': form,
                                                               'portfolio': form.cleaned_data['portfolio'],
                                                               'from_date': form.cleaned_data['from_date'],
                                                               'to_date': form.cleaned_data['to_date'],
                                                               'header': ['Name', 'Nominal', 'Price',
                                                                          'Last value', 'Dividends', 'Current value', 'Profit', 'ROI'],
                                                               'walk_through_header': ['name',
                                                                                       'nominal',
                                                                                       'price',
                                                                                       'value_at_beginning',
                                                                                       'dividends',
                                                                                       'value_at_end',
                                                                                       'profit', 'roi'],
                                                               'portfolio_content': content})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = PortfolioFormTwoDates()

    return render(request, 'portfolio_overview.html', {'block_title': 'Portfolio Overview',
                                                       'form': form})


def update_stocks_boerse_frankfurt(request):
    # import pdb; pdb.set_trace()
    p = Price()
    result = p.import_boerse_frankfurt()
    return render(request, 'import_quotes.html', {'block_title': 'Import Quotes from Börse Frankfurt', 'import_results': result})

def forecast_retirement(request):
    # import pdb; pdb.set_trace()
    m = Money()
    result = m.aggregate_results()
    return render(request, 'forecast_retirement.html', {'block_title': 'Forecast retirement', 'forecast_results': result})
