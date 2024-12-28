from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Transactions, CashBalance, Fees, Stocks
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import pandas as pd
import json
import logging
import os
from datetime import datetime, timedelta
from decimal import Decimal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3


from .forms import UserLoginForm, RegistrationForm
from django.contrib.auth.models import User

# Create your views here.

class StartView(View):
    def get(self, request):
        return render(request, 'start.html')

class MainView(View):
    def get(self, request):
        timestamp = datetime.now().timestamp()
        return render(request, 'main.html', {'timestamp': timestamp})

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
            return render(request, 'main.html', context)
        else:
            return render(request, 'login.html', context)

# def register(request):
#     if request.method =='POST':
#         form = RegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])
#             user.save()
#             return redirect('login')
#     else:
#         form = RegistrationForm()
#         return render(request, 'register.html', {'form': form})

class UserRegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('main.html')

    def form_valid(self, form):
        user = form.save()
        CashBalance.objects.create(user=user)
        login(self.request, user)
        return redirect('/../dashboard/')

class LogoutUserView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')

class DashboardView(View):
    def get(self, request):
            timestamp = datetime.now().timestamp()
            date = request.GET.get('date')
            exchange_filter = request.GET.get('exchange')
            page_number = request.GET.get('page', 1)
            cash_balance = None
            if request.user.is_authenticated:
                cash_balance = CashBalance.objects.get(user=request.user)
            if not date:
                return render(request, 'dashboard.html', {'rows': [], 'cash_balance': cash_balance, 'timestamp': timestamp})

            input_file = f'AlfaTrader_App/quotes/txt/{date}_d.txt'
            output_file = f'AlfaTrader_App/quotes/csv/{date}_d.csv'
            mapping_file = 'AlfaTrader_App/quotes/mapping/names_modified.csv'

            if not os.path.exists(input_file):
                return HttpResponse('txt file with latest quotes not found.', status=404)
            elif not os.path.exists(output_file):
                try:
                    df = pd.read_csv(input_file, sep=',')
                    df.to_csv(output_file, index=False)
                    upgraded_file = pd.merge(pd.read_csv(output_file), pd.read_csv(mapping_file), on='<TICKER>', how='left')
                    upgraded_file.to_csv(output_file, index=False)
                except Exception as error:
                    return HttpResponse(f'Error reading txt file: {error}', status=500)

            try:
                df = pd.read_csv(output_file)
                selected_columns = df.iloc[:, [0,10,2,7,11]]

                selected_columns.iloc[:, 3] = pd.to_numeric(selected_columns.iloc[:, 3], errors='coerce')
                if exchange_filter:
                    selected_columns = selected_columns[selected_columns['Exchange'] == exchange_filter]
                selected_columns.rename(columns={'<CLOSE>': 'CLOSE', '<TICKER>': 'TICKER', '<DATE>': 'DATE'}, inplace=True)
                paginator = Paginator(selected_columns, 20)
                page = paginator.get_page(page_number)
                rows = page.object_list.to_dict(orient='records')
            except Exception as error:
                return HttpResponse(f'Error reading csv file: {error}', status=500)

            return render(request, 'dashboard.html', {
                'rows': rows,
                'page': page,
                'paginator': paginator,
                'cash_balance': cash_balance
            })

## Alternatywny Dashboard
class DashboardView2(View):
    def get(self, request):
            timestamp = datetime.now().timestamp()
            exchange_filter = request.GET.get('exchange')
            page_number = request.GET.get('page', 1)
            cash_balance = None
            if request.user.is_authenticated:
                cash_balance = CashBalance.objects.get(user=request.user)

            today = datetime.today()
            if today.weekday() == 0:
                last_business_day = today - timedelta(days=3)
            else:
                last_business_day = today - timedelta(days=1)

            last_business_day_str = last_business_day.strftime('%Y%m%d')
            input_file = f'AlfaTrader_App/quotes/txt/{last_business_day_str}_d.txt'
            output_file = f'AlfaTrader_App/quotes/csv/{last_business_day_str}_d.csv'
            mapping_file = 'AlfaTrader_App/quotes/mapping/names_modified.csv'

            load_file = request.GET.get('load_file') == 'true'

            if not os.path.exists(input_file) and not load_file:
                return render(request, 'dashboard2.html', {
                    'cash_balance': cash_balance,
                    'timestamp': timestamp,
                    'error_message': f"Please save down the txt quotes file from https://stooq.pl/db/ for the date {last_business_day_str}."
                })
            elif load_file and not os.path.exists(input_file):
                return render(request, 'dashboard2.html', {
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
                    filtered_df = merged_df[merged_df['Exchange'].isin(valid_exchanges)]
                    filtered_df.to_csv(output_file, index=False)
                    # df.to_csv(output_file, index=False)
                    # upgraded_file = pd.merge(pd.read_csv(output_file), pd.read_csv(mapping_file), on='<TICKER>', how='left')
                    # upgraded_file.to_csv(output_file, index=False)
                except Exception as error:
                    return HttpResponse(f'Error reading txt file: {error}', status=500)

            try:
                df = pd.read_csv(output_file)
                selected_columns = df.iloc[:, [0,10,2,7,11]]

                selected_columns.iloc[:, 3] = pd.to_numeric(selected_columns.iloc[:, 3], errors='coerce')
                if exchange_filter:
                    selected_columns = selected_columns[selected_columns['Exchange'] == exchange_filter]
                selected_columns.rename(columns={'<CLOSE>': 'CLOSE', '<TICKER>': 'TICKER', '<DATE>': 'DATE'}, inplace=True)
                paginator = Paginator(selected_columns, 20)
                page = paginator.get_page(page_number)
                rows = page.object_list.to_dict(orient='records')
            except Exception as error:
                return HttpResponse(f'Error reading csv file: {error}', status=500)

            return render(request, 'dashboard2.html', {
                'rows': rows,
                'page': page,
                'paginator': paginator,
                'cash_balance': cash_balance
            })

## Dashboard pobierajacy dane z SQLite

# class DashboardView3(View):
#     def get(self, request):
#             timestamp = datetime.now().timestamp()
#             exchange_filter = request.GET.get('exchange')
#             page_number = request.GET.get('page', 1)
#             cash_balance = None
#             if request.user.is_authenticated:
#                 cash_balance = CashBalance.objects.get(user=request.user)
#
#             today = datetime.today()
#             if today.weekday() == 0:
#                 last_business_day = today - timedelta(days=3)
#             elif today.weekday() == 6:
#                 last_business_day = today - timedelta(days=2)
#             else:
#                 last_business_day = today - timedelta(days=1)
#
#             last_business_day_str = last_business_day.strftime('%Y%m%d')
#             input_file = f'AlfaTrader_App/quotes/txt/{last_business_day_str}_d.txt'
#             output_file = f'AlfaTrader_App/quotes/csv/{last_business_day_str}_d.csv'
#             mapping_file = 'AlfaTrader_App/quotes/mapping/names_modified.csv'
#
#             load_file = request.GET.get('load_file') == 'true'
#
#             if not os.path.exists(input_file) and not load_file:
#                 return render(request, 'dashboard3.html', {
#                     'cash_balance': cash_balance,
#                     'timestamp': timestamp,
#                     'error_message': f"Please save down the txt quotes file from https://stooq.pl/db/ for the date {last_business_day_str}."
#                 })
#             elif load_file and not os.path.exists(input_file):
#                 return render(request, 'dashboard3.html', {
#                     'cash_balance': cash_balance,
#                     'timestamp': timestamp,
#                     'error_message': f"You still have not pulled down the txt quotes file from https://stooq.pl/db/ for the date {last_business_day_str}, do it please."
#                 })
#             elif not os.path.exists(output_file):
#                 try:
#                     df = pd.read_csv(input_file, sep=',')
#                     mapping_df = pd.read_csv(mapping_file)
#                     merged_df = pd.merge(df, mapping_df, on='<TICKER>', how='left')
#                     valid_exchanges = ['GPW', 'NYSE', 'NASDAQ']
#                     print(f"Merged DataFrame before filtering: {merged_df}")
#                     filtered_df = merged_df[merged_df['Exchange'].isin(valid_exchanges)]
#                     print(f"Filtered DataFrame: {filtered_df}")
#
#                     stocks_to_save = []
#                     for _, row in filtered_df.iterrows():
#                         date_value = str(int(row['<DATE>']))
#                         try:
#                             date_parsed = datetime.strptime(date_value, '%Y%m%d').date()
#                         except ValueError:
#                             print(f"Skipping row with invalid date: {row['<DATE>']}")
#                             continue
#                         print(f"Preparing to save stock: {row['<TICKER>']}, {row['Name']}, {date_parsed}, {row['<CLOSE>']}")
#
#                         stock = Stocks(
#                             ticker=row['<TICKER>'],
#                             name=row['Name'],
#                             date=date_parsed,
#                             close=row['<CLOSE>'],
#                             exchange=row['Exchange'],
#                         )
#
#                         if not Stocks.objects.filter(ticker=stock.ticker, date=stock.date).exists():
#                             stocks_to_save.append(stock)
#                             print(f"Stock added to list: {stock.ticker} for date {stock.date}")
#                         else:
#                             print(f"Stcok already exist in database: {stock.ticker} for date {stock.date}")
#
#                     if stocks_to_save:
#                         Stocks.objects.bulk_create(stocks_to_save)
#                         print(f"Bulk saved {len(stocks_to_save)} stocks")
#                     else:
#                         print("No stocks to save")
#
#                     filtered_df.to_csv(output_file, index=False)
#
#                 except Exception as error:
#                     return HttpResponse(f'Error reading txt file: {error}', status=500)
#
#             try:
#                 stocks = Stocks.objects.filter(date=last_business_day).order_by('ticker')
#                 if exchange_filter:
#                     stocks = stocks.filter(exchange=exchange_filter)
#                 paginator = Paginator(stocks, 20)
#                 page = paginator.get_page(page_number)
#             except Exception as error:
#                 return HttpResponse(f'Error fetching data from the database: {error}', status=500)
#
#             return render(request, 'dashboard3.html', {
#                 'stocks': page.object_list,
#                 'page': page,
#                 'paginator': paginator,
#                 'cash_balance': cash_balance
#             })

class DashboardView3(View):
    def get(self, request):
            timestamp = datetime.now().timestamp()
            exchange_filter = request.GET.get('exchange')
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
                            print(f"Stcok already exist in database: {stock.ticker} for date {stock.date}")

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
                'cash_balance': cash_balance
            })

logger = logging.getLogger(__name__)

@method_decorator(login_required, name='dispatch')
class BuyTransactionView(View):
    def post(self, request):
        try:
            logger.debug(f"Request body: {request.body.decode('utf-8')}")
            if not request.body:
                logger.error("Empty request body.")
                return JsonResponse({'status': 'error', 'message': 'Empty request body.'}, status=400)
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

            ticker = data.get('stock_id')
            quantity = data.get('quantity')
            value = data.get('value')
            close = data.get('close')
            fee = data.get('fees')

            logger.debug(f"Recieved data: ticker={ticker}, quantity={quantity}, value={value}, close={close}, fee={fee}")

            if not ticker or not quantity or not value or not close or fee is None:
                logger.error("Missing data fields.")
                return JsonResponse({'status': "error", 'message': 'Missing data fields'}, status=400)


            try:
                quantity = int(quantity)
                value = Decimal(value)
                close = Decimal(close)
                fee = Decimal(fee)
            except ValueError as e:
                logger.error(f"Invalid value for quantity, value or close: {e}")
                return JsonResponse({'status': "error", 'message': 'Invalid value for quantity, value or close'}, status=400)

            transaction = Transactions.objects.create(
                ticker=ticker,
                quantity=quantity,
                transaction_type='BUY',
                value=value,
                close_price=close,
                user=request.user
            )

            logger.debug(f"Transaction created: {transaction}")

            Fees.objects.create(
                transaction_id=transaction,
                user=request.user,
                fee=fee
            )

            logger.debug(f"Fee entry created: {fee}")

            cash_balance = CashBalance.objects.get(user=request.user)
            cash_balance.balance -= value + fee
            cash_balance.save()
            logger.debug(f"Cash balance updated: {cash_balance.balance}")

            logger.debug(f"Transaction created successfully: {transaction}")

            return JsonResponse({'status': 'success', 'transaction_id': transaction.id})

        except Exception as e:
            logger.error(f"Error in BuyTransactionView: {e}")
            return JsonResponse({'status': 'error', 'message': 'an error occurred while processing the transaction.'}, status=500)

@method_decorator(login_required, name='dispatch')
class TransactionsView(View):
    def get(self, request):
        # Pobieranie wszystkich transakcji dla zalogowanego użytkownika
        cash_balance = CashBalance.objects.get(user=request.user)
        transactions = Transactions.objects.filter(user=request.user)
        fees = Fees.objects.filter(user=request.user).select_related('transaction_id')
        return render(request, 'transactions.html', {'transactions': transactions, 'fees': fees, 'cash_balance': cash_balance})

class TickerDetailsView(View):
    def get(self, request, ticker):
        timestamp = datetime.now().timestamp()
        transactions = Transactions.objects.filter(ticker=ticker, user=request.user)
        buy_transactions = transactions.filter(transaction_type='BUY')
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

        if buy_transactions.exists():
            total_value = sum(t.quantity * t.close_price for t in buy_transactions)
            total_quantity = sum(t.quantity for t in buy_transactions)
            weighted_avg_cost_price = total_value / total_quantity if total_quantity > 0 else 0
            weighted_avg_cost_price = round(weighted_avg_cost_price, 2)
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


        })

@method_decorator(login_required, name='dispatch')
class SellTransactionView(View):
    def post(self, request):
        pass




















