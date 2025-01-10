from django.contrib import admin

# Register your models here.

from AlfaTrader_App.models import Transactions, CashBalance, Fees, UserStocksBalance, Portfolio, PortfolioStocks

admin.site.register(Transactions)
admin.site.register(CashBalance)
admin.site.register(Fees)
admin.site.register(UserStocksBalance)
admin.site.register(Portfolio)
admin.site.register(PortfolioStocks)
