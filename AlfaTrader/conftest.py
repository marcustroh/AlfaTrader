from datetime import datetime

import pytest
from django.contrib.auth.models import User

from AlfaTrader_App.models import CashBalance, Stocks, Transactions, UserStocksBalance
from decimal import Decimal


@pytest.fixture
def user_cash(db):
    user = User.objects.create_user(username='testuser', password='userpassword')
    cash_balance = CashBalance.objects.create(user=user, balance=10000.00)
    return user, cash_balance

@pytest.fixture
def stock_price(db):
    stock = Stocks.objects.create(
        ticker='TEST',
        name='TestCompany',
        date='2025-01-03',
        close=Decimal('100.11'),
        exchange='NYSE',
    )
    return stock

@pytest.fixture
def transactions(db, user_cash):
    # Wykorzystanie uzytkownaika ktory jest jzu w fiksturze user_cash
    user, _ = user_cash
    buy_transaction = Transactions.objects.create(
        ticker='TEST',
        quantity=10,
        transaction_type='BUY',
        value=1000.00,
        close_price=Decimal('100.00'),
        user=user,
        date='2025-01-03',
    )
    buy_transaction2 = Transactions.objects.create(
        ticker='TEST',
        quantity=10,
        transaction_type='BUY',
        value=1030.00,
        close_price=Decimal('103.00'),
        user=user,
        date='2025-01-04',
    )
    sell_transaction = Transactions.objects.create(
        ticker='TEST',
        quantity=5,
        transaction_type='SELL',
        value=525.00,
        close_price=Decimal('105.00'),
        user=user,
        date='2025-01-05',
    )
    return [buy_transaction, buy_transaction2, sell_transaction]

@pytest.fixture
def user_stock_balance(db, user_cash, stock_price, transactions):
    user, _ = user_cash

    stock_balance = UserStocksBalance.objects.create(
        user=user,
        ticker=transactions[0].ticker,
        quantity='15',
        avg_cost_price='102.00',
    )
    return stock_balance

@pytest.fixture
def form_data(db, user_cash, user_stock_balance):
    user, _ = user_cash
    form_data = {
        'portfolio_name': 'My Portfolio',
        'stock': [user_stock_balance.id]
    }
    return form_data
















