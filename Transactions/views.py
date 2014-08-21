import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone

from Transactions.models import Transaction

# Create your views here.

def test(request):
# 	import pdb; pdb.set_trace()
	t = Transaction()

	return HttpResponse("Hello, world. You're at the Transactions Test." + str(t.get_total_for_portfolio('All')[0]))