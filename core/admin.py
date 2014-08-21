from django.contrib import admin

from Securities.models import Security, Price
from Money.models import Money
from Transactions.models import Transaction, Portfolio



# Register your models here.

class SecurityAdmin(admin.ModelAdmin):
    fields = ['name', 'aliases', 'type', 'isin_id', 'yahoo_id']


admin.site.register(Security, SecurityAdmin)
admin.site.register(Money)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(Price)