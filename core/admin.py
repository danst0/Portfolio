from django.contrib import admin

from Securities.models import Security, Price
from Money.models import Money
from Transactions.models import Transaction, Portfolio



# Register your models here.


admin.site.register(Money)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(Price)