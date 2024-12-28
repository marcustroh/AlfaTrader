from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Stocks(models.Model):
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    date = models.DateField()
    close = models.DecimalField(max_digits=10, decimal_places=2)
    exchange = models.CharField(max_length=10)

    class Meta:
        unique_together = ('ticker', 'date')

    def __str__(self):
        return f"{self.date} - {self.ticker} - {self.close}"

class Transactions(models.Model):
    ticker = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=(('BUY', 'Buy'), ('SELL', 'Sell')))
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

class Fees(models.Model):
    transaction_id = models.ForeignKey(Transactions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fee = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Fee for transaction {self.transaction_id.id} by user {self.user.username} (Fee: {self.fee})"

























