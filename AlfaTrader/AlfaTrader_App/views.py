from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login, logout
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import CashBalance, Fees, Stocks, Transactions, UserStocksBalance, Portfolio, PortfolioStocks
from .forms import PortfolioForm, PortfolioModifyForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import pandas as pd
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
from django.urls import reverse
from django.contrib import messages

from .forms import UserLoginForm, RegistrationForm
from django.contrib.auth.models import User

# Create your views here.

class StartView(View):
    def get(self, request):
        if request.user.is_authenticated:
            cash_balance = CashBalance.objects.get(user=request.user)
        else:
            cash_balance = None
        return render(request, 'start.html', {'cash_balance': cash_balance})

class BaseView(View):
    def get(self, request):
        return render(request, '__base__.html')

class UserLoginView(View):
    def get(self, request, *args, **kwargs):
        context = {
            'form': UserLoginForm()
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        context = {
            'form': form
        }
        if form.is_valid():
            login(request, form.user)
            return render(request, 'start.html', context)
        else:
            return render(request, 'login.html', context)

class UserRegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('start.html')

    def form_valid(self, form):
        user = form.save()
        CashBalance.objects.create(user=user)
        login(self.request, user)
        return redirect('/../')

class LogoutUserView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')

@method_decorator(login_required, name='dispatch')
class DashboardView3(View):
    def get(self, request):
            timestamp = datetime.now().timestamp()
            exchange_filter = request.GET.get('exchange')
            search_query = request.GET.get('search', '').strip()
            page_number = request.GET.get('page', 1)
            cash_balance = None

            if request.user.is_authenticated:
                cash_balance = CashBalance.objects.get(user=request.user)

            today = datetime.today()
            if today.weekday() == 0:
                last_business_day = today - timedelta(days=3)
            elif today.weekday() == 6:
                last_business_day = today - timedelta(days=2)
            else:
                last_business_day = today - timedelta(days=1)

            last_business_day_str = last_business_day.strftime('%Y%m%d')
            input_file = f'AlfaTrader_App/quotes/txt/{last_business_day_str}_d.txt'
            output_file = f'AlfaTrader_App/quotes/csv/{last_business_day_str}_d.csv'
            mapping_file = 'AlfaTrader_App/quotes/mapping/names_modified.csv'

            load_file = request.GET.get('load_file') == 'true'

            if not os.path.exists(input_file) and not load_file:
                return render(request, 'dashboard3.html', {
                    'cash_balance': cash_balance,
                    'timestamp': timestamp,
                    'error_message': f"Please save down the txt quotes file from https://stooq.pl/db/ for the date {last_business_day_str}."
                })
            elif load_file and not os.path.exists(input_file):
                return render(request, 'dashboard3.html', {
                    'cash_balance': cash_balance,
                    'timestamp': timestamp,
                    'error_message': f"You still have not pulled down the txt quotes file from https://stooq.pl/db/ for the date {last_business_day_str}, do it please."
                })
            elif not os.path.exists(output_file):
                try:
                    df = pd.read_csv(input_file, sep=',')
                    mapping_df = pd.read_csv(mapping_file)
                    merged_df = pd.merge(df, mapping_df, on='<TICKER>', how='left')
                    valid_exchanges = ['GPW', 'NYSE', 'NASDAQ']
                    print(f"Merged DataFrame before filtering: {merged_df}")
                    filtered_df = merged_df[merged_df['Exchange'].isin(valid_exchanges)]
                    print(f"Filtered DataFrame: {filtered_df}")

                    stocks_to_save = []
                    for _, row in filtered_df.iterrows():
                        date_value = str(int(row['<DATE>']))
                        try:
                            date_parsed = datetime.strptime(date_value, '%Y%m%d').date()
                        except ValueError:
                            print(f"Skipping row with invalid date: {row['<DATE>']}")
                            continue
                        print(f"Preparing to save stock: {row['<TICKER>']}, {row['Name']}, {date_parsed}, {row['<CLOSE>']}")

                        stock = Stocks(
                            ticker=row['<TICKER>'],
                            name=row['Name'],
                            date=date_parsed,
                            close=row['<CLOSE>'],
                            exchange=row['Exchange'],
                        )

                        if not Stocks.objects.filter(ticker=stock.ticker, date=stock.date).exists():
                            stocks_to_save.append(stock)
                            print(f"Stock added to list: {stock.ticker} for date {stock.date}")
                        else:
                            print(f"Stock already exist in database: {stock.ticker} for date {stock.date}")

                    if stocks_to_save:
                        Stocks.objects.bulk_create(stocks_to_save)
                        print(f"Bulk saved {len(stocks_to_save)} stocks")
                    else:
                        print("No stocks to save")

                    filtered_df.to_csv(output_file, index=False)

                except Exception as error:
                    return HttpResponse(f'Error reading txt file: {error}', status=500)

            try:
                stocks = Stocks.objects.filter(date=last_business_day).order_by('ticker')
                if exchange_filter:
                    stocks = stocks.filter(exchange=exchange_filter)

                if search_query:
                    stocks = stocks.filter(name__icontains=search_query)

                if not stocks.exists():
                    previous_business_day = last_business_day
                    while not stocks.exists():
                        previous_business_day -= timedelta(days=1)
                        while previous_business_day.weekday() in [5, 6]:
                            previous_business_day -= timedelta(days=1)

                        stocks = Stocks.objects.filter(date=previous_business_day).order_by('ticker')
                        if exchange_filter:
                            stocks = stocks.filter(exchange=exchange_filter)

                    print(f"Using data from previous business day: {previous_business_day.strftime('%Y-%m-%d')}")

                paginator = Paginator(stocks, 20)
                page = paginator.get_page(page_number)

            except Exception as error:
                return HttpResponse(f'Error fetching data from the database: {error}', status=500)

            if not stocks.exists():
                page = []

            return render(request, 'dashboard3.html', {
                'stocks': page.object_list if isinstance(page, Paginator) else page,
                'page': page,
                'paginator': paginator,
                'cash_balance': cash_balance,
                'timestamp': timestamp
            })

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class BuyTransactionView(View):
    def post(self, request):
        try:
            close_price = request.POST['close_price_buy']
            cost_price = request.POST['cost_price']
            quantity_buy = Decimal(request.POST['quantity_buy'])
            value = Decimal(request.POST['value_buy'])
            fee = Decimal(request.POST['fee_buy'])
            user = request.user
            ticker = request.POST['ticker']
        except Exception as error:
            return HttpResponse(f'Error reading data from the form: {error}', status=500)

        try:
            cash_balance = CashBalance.objects.get(user=request.user)

            total_cost = value + fee

            if cash_balance.balance < total_cost:
                messages.error(request, 'Insufficent funds for this transaction.')
                redirect_url = reverse('ticker_detail', kwargs={'ticker': ticker})
                return HttpResponseRedirect(redirect_url)

            # with transaction.atomic():

            transaction = Transactions.objects.create(
                ticker=ticker,
                quantity=quantity_buy,
                transaction_type='BUY',
                value=value,
                close_price=close_price,
                user=user
            )

            logger.debug(f"Transaction created: {transaction}")

            Fees.objects.create(
                transaction_id=transaction,
                user=request.user,
                fee=fee
            )

            cash_balance = CashBalance.objects.get(user=request.user)
            cash_balance.balance -= value + fee
            cash_balance.save()

            user_stock_balance, created = UserStocksBalance.objects.get_or_create(
                user=user,
                ticker=ticker,
                defaults={'quantity': 0, 'avg_cost_price': close_price}
            )

            if not created:
                user_stock_balance.avg_cost_price = cost_price

            user_stock_balance.quantity += quantity_buy
            user_stock_balance.save()

            messages.success(request, 'Transaction created successfully!')

        except Exception as error:
            return HttpResponse(f'Error saving data the database: {error}', status=500)


        redirect_url = reverse('ticker_detail', kwargs={'ticker': ticker})
        return HttpResponseRedirect(redirect_url)


@method_decorator(login_required, name='dispatch')
class TransactionsView(View):
    def get(self, request):
        # Pobieranie wszystkich transakcji dla zalogowanego użytkownika
        cash_balance = CashBalance.objects.get(user=request.user)
        transactions = Transactions.objects.filter(user=request.user)
        fees = Fees.objects.filter(user=request.user).select_related('transaction_id')
        return render(request, 'transactions.html', {'transactions': transactions, 'fees': fees, 'cash_balance': cash_balance})

@method_decorator(login_required, name='dispatch')
class TickerDetailsView(View):
    def get(self, request, ticker):
        timestamp = datetime.now().timestamp()
        transactions = Transactions.objects.filter(ticker=ticker, user=request.user)
        buy_transactions = transactions.filter(transaction_type='BUY').order_by('date')
        cash_balance = CashBalance.objects.get(user=request.user)
        today = datetime.today()

        if today.weekday() == 0:
            last_business_day = today - timedelta(days=3)
        elif today.weekday() == 6:
            last_business_day = today - timedelta(days=2)
        else:
            last_business_day = today - timedelta(days=1)

        last_business_day_str = last_business_day.strftime('%Y%m%d')

        try:
            close_price_set = None
            while close_price_set is None:
                close_price_set = Stocks.objects.filter(ticker=ticker, date=last_business_day_str).first()
                if close_price_set:
                    break
                else:
                    last_business_day -= timedelta(days=1)
                    while last_business_day.weekday() in [5, 6]:
                        last_business_day -= timedelta(days=1)
                    last_business_day_str = last_business_day.strftime('%Y%m%d')

            if close_price_set:
                close_price = close_price_set.close
            else:
                close_price = None

        except Exception as error:
            return HttpResponse(f"Error fetching close price: {error}", status=500)


        remaining_shares = 0
        weighted_sum = 0
        if buy_transactions.exists():
            for buy in buy_transactions:
                remaining_shares += buy.quantity
                weighted_sum += buy.quantity * buy.close_price

            sell_transactions = transactions.filter(transaction_type='SELL')

            if sell_transactions.exists():
                for sell in sell_transactions:
                    sell_quantity = sell.quantity
                    for buy in buy_transactions:
                        if sell_quantity <= 0:
                            break
                        if buy.quantity > 0:
                            if buy.quantity <= sell_quantity:
                                sell_quantity -= buy.quantity
                                weighted_sum -= buy.quantity * buy.close_price
                                remaining_shares -= buy.quantity
                                buy.quantity = 0
                            else:
                                buy.quantity -= sell_quantity
                                weighted_sum -= sell_quantity * buy.close_price
                                remaining_shares -= sell_quantity
                                sell_quantity = 0

            if remaining_shares > 0:
                weighted_avg_cost_price = weighted_sum / remaining_shares
                weighted_avg_cost_price = round(weighted_avg_cost_price, 2)
            else:
                weighted_avg_cost_price = 0
        else:
            weighted_avg_cost_price = 0

        #pobieranie danych dla danego tickera
        stock_data = Stocks.objects.filter(ticker=ticker).order_by('date')

        if not stock_data:
            return render(request, 'ticker_details.html', {
                                    'transactions': transactions,
                                    'cash_balance': cash_balance,
                                    'ticker': ticker,
                                    'error_message': 'No stock data found for this ticker'
            })
        #Przygotowanie danych do wykresu
        dates = [stock.date for stock in stock_data]
        close_prices = [stock.close for stock in stock_data]

        #Tworzenie wykresu
        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(dates, close_prices, label='Close Price', color='blue')
        ax.set_title(f"{ticker} Stock Price Over Time")
        ax.set_xlabel('Date')
        ax.set_ylabel('Close Price')
        ax.grid(True)
        ax.legend()

        #Konwersja wykresu na html
        graph_html = mpld3.fig_to_html(fig)

        return render(request, 'ticker_details.html', {
            'transactions': transactions,
            'cash_balance': cash_balance,
            'ticker': ticker,
            'close_price': close_price,
            'weighted_avg_cost_price': weighted_avg_cost_price,
            'graph_html': graph_html,
            'timestamp': timestamp,
            'remaining_shares': remaining_shares,


        })

@method_decorator(login_required, name='dispatch')
class SellTransactionView(View):
    def post(self, request):
        try:
            quantity_sell = Decimal(request.POST['quantity_sell'])
            close_price = request.POST['close_price_sell']
            cost_price = request.POST['cost_price']
            ticker = request.POST['ticker']
            value = Decimal(request.POST['value_sell'])
            user = request.user
            fee = Decimal(request.POST['fees_sell'])
            remaining_shares = request.POST['remaining_shares']

        except Exception as error:
            return HttpResponse(f'Error reading data from the form: {error}', status=500)

        try:
            transaction = Transactions.objects.create(
                ticker=ticker,
                quantity=quantity_sell,
                transaction_type='SELL',
                value=value,
                close_price=close_price,
                user=user
            )

            Fees.objects.create(
                transaction_id=transaction,
                user=request.user,
                fee=fee
            )

            cash_balance = CashBalance.objects.get(user=request.user)
            cash_balance.balance += value - fee
            cash_balance.save()

            user_stock_balance, created = UserStocksBalance.objects.get_or_create(
                user=user,
                ticker=ticker,
            )

            user_stock_balance.avg_cost_price = close_price
            user_stock_balance.quantity -= quantity_sell
            user_stock_balance.save()

            messages.success(request, 'Transaction created successfully!')

        except Exception as error:
            return HttpResponse(f'Error saving data the database: {error}', status=500)

        redirect_url = reverse('ticker_detail', kwargs={'ticker': ticker})
        return HttpResponseRedirect(redirect_url)

class AboutAuthor(View):
    def get(self, request):
        if request.user.is_authenticated:
            cash_balance = CashBalance.objects.get(user=request.user)
        else:
            cash_balance = None
        return render(request, 'author.html', {'cash_balance': cash_balance})

class ContactDetails(View):
    def get(self, request):
        if request.user.is_authenticated:
            cash_balance = CashBalance.objects.get(user=request.user)
        else:
            cash_balance = None
        return render(request, 'contact_details.html', {'cash_balance': cash_balance})

class AboutApp(View):
    def get(self, request):
        if request.user.is_authenticated:
            cash_balance = CashBalance.objects.get(user=request.user)
        else:
            cash_balance = None
        return render(request, 'about_app.html', {'cash_balance': cash_balance})

class HowToBegin(View):
    def get(self, request):
        if request.user.is_authenticated:
            cash_balance = CashBalance.objects.get(user=request.user)
        else:
            cash_balance = None
        return render(request, 'how_to_begin.html', {'cash_balance': cash_balance})


@method_decorator(login_required, name='dispatch')
class PortfoliosView(View):
    def get(self, request):
        portfolios = Portfolio.objects.filter(user=request.user)
        cash_balance = CashBalance.objects.get(user=request.user)

        portfolios_data = []
        for portfolio in portfolios:
            portfolio_stocks = PortfolioStocks.objects.filter(portfolio=portfolio)
            stocks_with_quantities = []
            for portfolio_stock in portfolio_stocks:
                stock = portfolio_stock.stocks
                ticker = stock.ticker

                last_stock = Stocks.objects.filter(ticker=ticker).order_by('-date').first()
                last_close_price = last_stock.close if last_stock else None

                # user_cost_price = UserStocksBalance.objects.filter(user=request.user, ticker=ticker).first()
                # cost_price = user_cost_price.avg_cost_price if user_cost_price else None

                transactions = Transactions.objects.filter(ticker=ticker, user=request.user)
                buy_transactions = transactions.filter(transaction_type='BUY').order_by('date')
                sell_transactions = transactions.filter(transaction_type='SELL')
                remaining_shares = 0
                weighted_sum = 0
                if buy_transactions.exists():
                    for buy in buy_transactions:
                        remaining_shares += buy.quantity
                        weighted_sum += buy.quantity * buy.close_price

                    sell_transactions = transactions.filter(transaction_type='SELL')

                    if sell_transactions.exists():
                        for sell in sell_transactions:
                            sell_quantity = sell.quantity
                            for buy in buy_transactions:
                                if sell_quantity <= 0:
                                    break
                                if buy.quantity > 0:
                                    if buy.quantity <= sell_quantity:
                                        sell_quantity -= buy.quantity
                                        weighted_sum -= buy.quantity * buy.close_price
                                        remaining_shares -= buy.quantity
                                        buy.quantity = 0
                                    else:
                                        buy.quantity -= sell_quantity
                                        weighted_sum -= sell_quantity * buy.close_price
                                        remaining_shares -= sell_quantity
                                        sell_quantity = 0

                    if remaining_shares > 0:
                        cost_price = weighted_sum / remaining_shares
                        cost_price = round(cost_price, 2)
                    else:
                        cost_price = 0
                else:
                    cost_price = 0

                profit_loss = None
                if last_close_price is not None and cost_price is not None:
                    profit_loss = stock.quantity * (last_close_price - cost_price)

                stocks_with_quantities.append({
                    'ticker': stock.ticker,
                    'quantity': stock.quantity,
                    'close_price': last_close_price,
                    'cost_price': cost_price,
                    'profit_loss': profit_loss
                })
            portfolios_data.append({
                'portfolio': portfolio,
                'stocks': stocks_with_quantities
            })

        return render(request, 'portfolios.html', {
            'portfolios_data': portfolios_data,
            'cash_balance': cash_balance,
        })

@method_decorator(login_required, name='dispatch')
class PortfolioCreateView(View):
    def get(self, request):
        form = PortfolioForm(user=request.user)
        cash_balance = CashBalance.objects.get(user=request.user)
        return render(request, 'portfolio_create.html', {'form': form, 'cash_balance': cash_balance})
    def post(self, request):
        form = PortfolioForm(request.POST)

        if form.is_valid():
            portfolio_name = form.cleaned_data['portfolio_name']
            selected_stocks = form.cleaned_data['stock']

            portfolio = Portfolio.objects.create(
                user=request.user,
                name=portfolio_name,
            )

            for stock in selected_stocks:
                PortfolioStocks.objects.create(
                    portfolio=portfolio,
                    stocks=stock
                )

            return render(request, 'portfolios.html')

        return render(request, 'portfolios.html')

@method_decorator(login_required, name='dispatch')
class PortfolioModifyView(UpdateView):
    model = Portfolio
    form_class = PortfolioModifyForm
    template_name = 'portfolio_create.html'

    def get_success_url(self):
        return reverse_lazy('portfolios')

    def get_object(self, queryset=None):
        return get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'], user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        portfolio = form.save(commit=False)
        portfolio.save()

        PortfolioStocks.objects.filter(portfolio=portfolio).delete()

        selected_stocks = form.cleaned_data['stocks']
        for stock in selected_stocks:
            PortfolioStocks.objects.create(portfolio=portfolio, stocks=stock)

        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class PortfolioDeleteView(DeleteView):
    model = Portfolio
    template_name = 'portfolio_delete_confirm.html'
    context_object_name = 'portfolio'

    def get_object(self, queryset=None):
        return get_object_or_404(Portfolio, id=self.kwargs['portfolio_id'], user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('portfolios')


























