from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from core.forms import RollingProfitabilityForm
from core.models import UI

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import datetime
import random
from django.http import HttpResponse

# Create your views here.



def index(request):
    return render(request, 'index.html')


def update(request):
    #return HttpResponse("Hello, world. You're at the m2/update index.")
    return render(request, 'update.html')

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
        form = RollingProfitabilityForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            pic_url = 'http://localhost:8000/core/' + \
                      form.cleaned_data['portfolio'] + '/' + \
                      form.cleaned_data['from_date'].strftime('%Y-%m-%d') + '/' + \
                      form.cleaned_data['to_date'].strftime('%Y-%m-%d') +\
                      '/diagram.png'
            content = 'You are great <a href="http://google.com">so great</a>'
            return render(request, 'rolling_profitability.html', {'block_title': 'Rolling Profitability',
                                                                  'form': form,
                                                                  'content': content,
                                                                  'portfolio': form.cleaned_data['portfolio'],
                                                                  'from_date': form.cleaned_data['from_date'].strftime('%Y-%m-%d'),
                                                                  'to_date': form.cleaned_data['to_date'].strftime('%Y-%m-%d')})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = RollingProfitabilityForm()

    return render(request, 'rolling_profitability.html', {'block_title': 'Rolling Profitability',
                                                          'form': form})