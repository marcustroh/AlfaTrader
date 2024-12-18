from django.contrib import admin

# Register your models here.

from AlfaTrader_App.models import Transactions, CashBalance, Fees

admin.site.register(Transactions)
admin.site.register(CashBalance)
admin.site.register(Fees)
