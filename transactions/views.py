from django.shortcuts import render
from django.http import HttpResponse

from transactions.models import Transaction

# Create your views here.


def update(request):
    # import pdb; pdb.set_trace()
    t = Transaction()
    result = t.import_sources()
    return render(request, 'update.html', {'block_title': 'Import PDFs', 'import_results': result})
