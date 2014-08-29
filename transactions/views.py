from django.shortcuts import render
from django.http import HttpResponse

from transactions.models import Transaction

# Create your views here.


def update(request):
    # import pdb; pdb.set_trace()
    t = Transaction()
    t.import_sources()
    return render(request, 'update.html')