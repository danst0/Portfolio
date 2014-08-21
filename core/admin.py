from django.contrib import admin
from m2.models import Security
from m2.models import Money
from m2.models import Transaction
from m2.models import Price

# Register your models here.

class SecurityAdmin(admin.ModelAdmin):
    fields = ['name', 'aliases', 'type', 'isin_id', 'yahoo_id']

admin.site.register(Security, SecurityAdmin)
admin.site.register(Money)
admin.site.register(Transaction)
admin.site.register(Price)