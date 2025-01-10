from datetime import datetime, timedelta

from django.test import TestCase
import pytest
from django.urls import reverse
from django.contrib import messages
from .forms import PortfolioForm

from .models import User, CashBalance, Stocks, Fees, Portfolio, PortfolioStocks
from decimal import Decimal
from unittest.mock import patch

from AlfaTrader_App.forms import UserLoginForm

@pytest.mark.django_db
def test_user_register_view_valid_data(client):
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'email': 'newuser@gmail.com',
        'password': 'newpassword',
        'password_confirm': 'newpassword'
    })
    assert response.status_code == 302
    assert response.url == reverse('start')

    user = User.objects.get(username='newuser')
    assert user.email == 'newuser@gmail.com'
    # sprawdzenie czy haslo zostalo zahashowane
    assert user.check_password('newpassword')
    # sprawdzenie czy haslo nie zostalo zapisane w czystej postaci
    assert not user.password == 'securepassword'
    assert user.check_password('newpassword')
    assert user.is_authenticated
    cash_balance = CashBalance.objects.get(user=user)
    assert cash_balance.balance == 10000

@pytest.mark.django_db
def test_user_register_view_invalid_data(client):
    response = client.post(reverse('register'), {
        'newuser': 'newuser',
        'email': 'newuser@gmail.com',
        'password': 'newpassword',
        'password_confirm': 'differentpassword'
    })
    assert response.status_code == 200
    assert 'form' in response.context
    assert 'Passwords are not the same!' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_user_login_view(client):
    response = client.get(reverse('login'))
    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], UserLoginForm)

@pytest.mark.django_db
def test_login_view_post_valid_data(client, user_cash):
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'userpassword'
    })
    assert 'form' in response.context
    assert response.context['user'].is_authenticated
    assert reverse('start')

@pytest.mark.django_db
def test_login_view_post_invalid_data(client, user_cash):
    response = client.post(reverse('login'), {
                                   'username': 'testuser',
                                   'password': 'wrongpassword'
                               })
    assert response.status_code == 200
    assert 'form' in response.context
    assert not response.context['form'].is_valid()
    assert not response.context['user'].is_authenticated
    assert 'Incorrect password or login!' in response.content.decode('utf-8')

@pytest.mark.django_db
def test_user_logout_view(client, user_cash):
    client.login(username='testuser', password='userpassword')
    response = client.get(reverse('logout'))
    assert response.status_code == 302
    assert response.url == reverse('start')


@pytest.mark.django_db
def test_start_view_authenticated(client, user_cash):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')
    response = client.get(reverse('start'))

    assert response.status_code == 200
    assert response.context['cash_balance'] == cash_balance.balance

@pytest.mark.django_db
def test_start_view_anonymous(client, user_cash):
    response = client.get(reverse('start'))

    assert response.status_code == 200
    assert response.context['cash_balance'] is None

@pytest.mark.django_db
def test_dashboard3_view_authenticated_no_input_file(client, user_cash):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')

    with patch('os.path.exists', return_value=False):
        response = client.get(reverse('dashboard3'))
        assert response.status_code == 200

        last_business_day_str = (datetime.today() - timedelta(days=1)).strftime('%Y%m%d')
        expected_message = f"Please save down the txt quotes file from https://stooq.pl/db/ for the date {last_business_day_str}."
        assert response.context['error_message'] == expected_message

        assert response.context['cash_balance'] == cash_balance.balance
        assert 'stocks' not in response.context

@pytest.mark.django_db
def test_dashboard3_view_authenticated_with_input_file(client, user_cash, stock_price):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')

    with patch('os.path.exists', return_value=True):
        response = client.get(reverse('dashboard3'))
        assert response.status_code == 200

        assert 'error_message' not in response.context
        assert response.context['cash_balance'] == cash_balance.balance
        assert 'stocks' in response.context
        stocks = response.context['stocks']
        assert len(stocks) > 0
        assert stocks[0].ticker == stock_price.ticker


@pytest.mark.django_db
def test_dashboard3_view_anonymous(client, user_cash):
    response = client.get(reverse('dashboard3'))

    assert response.status_code == 302
    assert '/login/?next=' + reverse('dashboard3')
    response = client.get(reverse('login'))
    assert 'cash_balance' not in response.context

@pytest.mark.django_db
def test_ticker_details_view_authorized(client, user_cash, stock_price, transactions):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')
    response = client.get(reverse('ticker_detail', args=[stock_price.ticker]))
    assert response.status_code == 200
    assert response.context['cash_balance'] == cash_balance.balance
    assert response.context['close_price'] == stock_price.close
    assert response.context['ticker'] == stock_price.ticker
    assert response.context['weighted_avg_cost_price'] == round(Decimal(102.00), 2)
    assert response.context['remaining_shares'] == 15
    assert list(response.context['transactions']) == transactions
    assert 'graph_html' in response.context
    assert 'remaining_shares' in response.context

@pytest.mark.django_db
def test_ticker_details_view_not_authorized(client, user_cash, stock_price):
    response = client.get(reverse('ticker_detail', args=[stock_price.ticker]))
    assert response.status_code == 302
    assert '/login/?next=' + reverse('ticker_detail', args=[stock_price.ticker])
    response = client.get(reverse('login'))
    assert 'cash_balance' not in response.context

@pytest.mark.django_db
def test_buy_transaction_with_sufficient_funds(client, user_cash, transactions, user_stock_balance, stock_price):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')
    stock = Stocks.objects.get(ticker='TEST', date='2025-01-03')
    data = {
        'ticker': stock.ticker,
        'close_price_buy': str(stock.close),
        'cost_price': '102',
        'quantity_buy': '10',
        'value_buy': str(Decimal('1001.10')),
        'fee_buy': str(Decimal('10.00'))
    }
    response = client.post(reverse('buy_transaction'), data)
    assert response.status_code == 302
    assert response.url == reverse('ticker_detail', kwargs={'ticker': stock.ticker})

    messages_list = list(messages.get_messages(response.wsgi_request))
    assert len(messages_list) > 0
    assert messages_list[0].message == 'Transaction created successfully!'

    cash_balance.refresh_from_db()
    assert cash_balance.balance == Decimal('8988.90')

    user_stock_balance.refresh_from_db()
    assert user_stock_balance.quantity == 25
    assert user_stock_balance.avg_cost_price == Decimal('102.00')

    fee = Fees.objects.get(transaction_id__ticker=stock.ticker, user=user)
    assert fee.fee == Decimal('10.00')
    assert fee.transaction_id.ticker == stock.ticker

@pytest.mark.django_db
def test_buy_transaction_with_insufficient_funds(client, user_cash, transactions, user_stock_balance, stock_price):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')
    cash_balance.balance = Decimal('5.00')
    cash_balance.save()
    stock = Stocks.objects.get(ticker='TEST', date='2025-01-03')
    data = {
        'ticker': stock.ticker,
        'close_price_buy': str(stock.close),
        'cost_price': '102',
        'quantity_buy': '10',
        'value_buy': str(Decimal('1001.10')),
        'fee_buy': str(Decimal('10.00'))
    }

    response = client.post(reverse('buy_transaction'), data)
    assert response.status_code == 302
    assert response.url == reverse('ticker_detail', kwargs={'ticker': stock.ticker})

    messages_list = list(messages.get_messages(response.wsgi_request))
    assert len(messages_list) > 0
    assert messages_list[0].message == 'Insufficent funds for this transaction.'

    cash_balance.refresh_from_db()
    assert cash_balance.balance == Decimal('5.00')

    user_stock_balance.refresh_from_db()
    assert user_stock_balance.quantity == 15
    assert user_stock_balance.avg_cost_price == Decimal('102.00')

@pytest.mark.django_db
def test_sell_transaction_with_sufficient_shares(client, user_cash, transactions, user_stock_balance, stock_price):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')

    data = {
        'ticker': stock_price.ticker,
        'close_price_sell': str(stock_price.close),
        'cost_price': str(user_stock_balance.avg_cost_price),
        'quantity_sell': '10',
        'value_sell': str(Decimal('1001.10')),
        'fees_sell': str(Decimal('10.00')),
        'remaining_shares': '5'
    }

    response = client.post(reverse('sell_transaction'), data)
    assert response.status_code == 302
    assert response.url == reverse('ticker_detail', kwargs={'ticker': stock_price.ticker})

    messages_list = list(messages.get_messages(response.wsgi_request))
    assert len(messages_list) > 0
    assert messages_list[0].message == 'Transaction created successfully!'

    cash_balance.refresh_from_db()
    assert cash_balance.balance == Decimal('10991.10')

    user_stock_balance.refresh_from_db()
    assert user_stock_balance.quantity == 5
    assert user_stock_balance.avg_cost_price == Decimal('100.11')

    fee = Fees.objects.get(transaction_id__ticker=stock_price.ticker, user=user)
    assert fee.fee == Decimal('10.00')
    assert fee.transaction_id.ticker == stock_price.ticker


@pytest.mark.django_db
def test_portfolios_view_authenticated(client, user_cash):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')
    response = client.get(reverse('portfolios'))

    assert response.status_code == 200
    assert response.context['cash_balance'] == cash_balance.balance

@pytest.mark.django_db
def test_portfolios_view_anonymous(client, user_cash):
    response = client.get(reverse('portfolios'))

    assert response.status_code == 302
    assert '/login/?next=' + reverse('portfolios')
    response = client.get(reverse('login'))
    assert 'cash_balance' not in response.context

@pytest.mark.django_db
def test_transactions_view_authenticated(client, user_cash):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')
    response = client.get(reverse('transactions'))

    assert response.status_code == 200
    assert response.context['cash_balance'] == cash_balance.balance

@pytest.mark.django_db
def test_transactions_view_anonymous(client, user_cash):
    response = client.get(reverse('transactions'))

    assert response.status_code == 302
    assert '/login/?next=' + reverse('transactions')
    response = client.get(reverse('login'))
    assert 'cash_balance' not in response.context

def test_portfolio_create_view_get(client, user_cash, stock_price):
    user, cash_balance = user_cash
    client.login(username='testuser', password='userpassword')

    response = client.get(reverse('portfolio_create'))

    assert response.status_code == 200

    assert 'form' in response.context
    assert isinstance(response.context['form'], PortfolioForm)

    assert 'cash_balance' in response.context
    assert response.context['cash_balance'] == cash_balance.balance

@pytest.mark.django_db
def test_portfolio_create_view_post(client, user_cash, user_stock_balance, form_data):
    user, _ = user_cash
    client.login(username='testuser', password='userpassword')

    response = client.post(reverse('portfolio_create'), data=form_data)

    assert response.status_code == 200

    portfolio = Portfolio.objects.get(user=user)
    assert portfolio.name == form_data['portfolio_name']
    assert portfolio.user == user

    # Sprawdzenie, czy akcje zostały przypisane do portfela
    portfolio_stock = PortfolioStocks.objects.get(portfolio=portfolio)
    assert portfolio_stock.stocks == user_stock_balance

@pytest.mark.django_db
def test_portfolio_create_view_post_invalid_data(client, user_cash, user_stock_balance):
    user, _ = user_cash
    client.login(username='testuser', password='userpassword')

    invalid_data = {
        'portfolio_name': '',
        'stock': []
    }

    response = client.post(reverse('portfolio_create'), data=invalid_data)

    assert response.status_code == 200
    assert 'portfolios.html' in response.templates[0].name

    assert Portfolio.objects.filter(user=user).count() == 0
    assert PortfolioStocks.objects.count() == 0

@pytest.mark.django_db
def test_portfolio_modify_view_get(client, user_cash, user_stock_balance):
    user, _ = user_cash
    client.login(username='testuser', password='userpassword')

    portfolio = Portfolio.objects.create(user=user, name='My Portfolio')
    portfolio_stocks = PortfolioStocks.objects.create(portfolio=portfolio, stocks=user_stock_balance)

    response = client.get(reverse('portfolio_modify', kwargs={'portfolio_id': portfolio.id}))

    assert response.status_code == 200
    assert 'form' in response.context
    assert response.context['form'].instance == portfolio
    assert portfolio_stocks.stocks is not None
    assert portfolio_stocks.stocks == user_stock_balance

@pytest.mark.django_db
def test_portfolio_modify_view_post_valid_data(client, user_cash, user_stock_balance):
    user, _ = user_cash
    client.login(username='testuser', password='userpassword')
    portfolio = Portfolio.objects.create(user=user, name='My Portfolio')
    portfolio_stocks = PortfolioStocks.objects.create(portfolio=portfolio, stocks=user_stock_balance)

    form_data = {
        'name': 'Updated Portfolio',
        'stocks': [user_stock_balance.id]
    }

    response = client.post(reverse('portfolio_modify', kwargs={'portfolio_id': portfolio.id}), data=form_data)

    portfolio.refresh_from_db()
    assert portfolio.name == 'Updated Portfolio'
    assert portfolio_stocks.stocks == user_stock_balance

    assert response.status_code == 302
    assert response.url == reverse('portfolios')

@pytest.mark.django_db
def test_portfolio_modify_view_post_invalid_data(client, user_cash, stock_price, user_stock_balance):
    user, _ = user_cash
    client.login(username='testuser', password='userpassword')
    portfolio = Portfolio.objects.create(user=user, name='My Portfolio')
    PortfolioStocks.objects.create(portfolio=portfolio, stocks=user_stock_balance)
    form_data = {
        'name': 'Updated Portfolio',
        'stocks': []  # Brak wybranych akcji
    }

    response = client.post(reverse('portfolio_modify', kwargs={'portfolio_id': portfolio.id}), data=form_data)

    portfolio.refresh_from_db()
    assert portfolio.name == 'My Portfolio'  # Nazwa portfela nie powinna się zmienić

    assert response.status_code == 200
    assert 'form' in response.context
    messages_list = list(messages.get_messages(response.wsgi_request))
    assert len(messages_list) > 0
    assert messages_list[0].message == 'Please select stocks you want to add.'

@pytest.mark.django_db
def test_portfolio_delete_view(client, user_cash):
    user, _ = user_cash
    client.login(username='testuser', password='userpassword')
    portfolio = Portfolio.objects.create(user=user, name='My Portfolio')

    assert Portfolio.objects.count() == 1

    # Zrób żądanie DELETE, które ma usunąć portfolio
    response = client.post(reverse('portfolio_delete', kwargs={'portfolio_id': portfolio.id}))

    assert Portfolio.objects.count() == 0

    assert response.status_code == 302
    assert response.url == reverse('portfolios')




















