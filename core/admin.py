from django.contrib import admin

from securities.models import Price
from money.models import Money
from transactions.models import Transaction, Portfolio

# Register your models here.

admin.site.register(Money)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(Price)

