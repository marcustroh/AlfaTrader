from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Transactions(models.Model):
    ticker = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=10, decimal_places=2)
    close_price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.ticker} - {self.quantity} shares."

class CashBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=10000.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cash balance: {self.balance}"

























