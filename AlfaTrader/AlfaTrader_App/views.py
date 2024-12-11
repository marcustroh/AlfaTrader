from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
import requests
from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
from requests_html import AsyncHTMLSession
import nest_asyncio
import os
from django.conf import settings


from .forms import UserLoginForm, RegistrationForm
from django.contrib.auth.models import User

# Create your views here.

class MainView(View):
    def get(self, request):
        return render(request, 'main.html')

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
            return render(request, 'dashboard.html', context)

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
        login(self.request, user)
        return redirect('__base__.html')

class LogoutUserView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('/')

# class DashboardView(View):
#     def get(self, request):
#         url = 'https://stooq.pl/t/?i=513'
#         response = requests.get(url)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, 'html.parser')
#         table = soup.find('table')
#         dataframe = pd.read_html(str(table))
#         return render(request, 'dashboard.html', {'dataframe': dataframe})

# class DashboardView(View):
#     def get(self, request):
#         url = 'https://stooq.pl/t/?i=513'
#
#         response = requests.get(url)
#         response.raise_for_status()
#
#         soup = BeautifulSoup(response.text, 'html.parser')
#
#         rows = soup.find_all('tr')
#
#         data = []
#
#         for row in rows[1:]:
#             cols = row.find_all('td')
#             if len(cols) > 0:
#                 cols = [col.text.strip() if col.text.strip() else None for col in cols]
#                 data.append(cols)
#
#         if data:
#             dataframe = pd.DataFrame(data, columns=['Symbol', 'Nazwa', 'Otwarcie', 'Max', 'Min', 'Kurs', 'Zmiana', 'Wolumen',
#                                              'Obrot', 'Data'])
#
#         return render(request, 'dashboard.html', {'dataframe': dataframe})

# ZACIAGA DANE ZE STRONY ALE NIE PELNE
# class DashboardView(View):
#     def get(self, request):
#         url = 'https://stooq.pl/q/?s=06n&d=20241206'
#
#         response = requests.get(url)
#         html_content = response
#
#         return render(request, 'dashboard.html', {'dataframe': html_content})
# nest_asyncio.apply()

# class DashboardView(View):
#     def get(self, request):
#             date = request.GET.get('date')
#             exchange_filter = request.GET.get('exchange')
#             page_number = request.GET.get('page', 1)
#             search_query = request.GET.get('search', "")
#             if not date:
#                 return render(request, 'dashboard.html', {'rows': []})
#
#             input_file = f'AlfaTrader_App/quotes/txt/{date}_d.txt'
#             output_file = f'AlfaTrader_App/quotes/csv/{date}_d.csv'
#             mapping_file = 'AlfaTrader_App/quotes/mapping/names_modified.csv'
#
#             if not os.path.exists(input_file):
#                 return HttpResponse('txt file with latest quotes not found.', status=404)
#             elif not os.path.exists(output_file):
#                 try:
#                     df = pd.read_csv(input_file, sep=',')
#                     df.to_csv(output_file, index=False)
#                     upgraded_file = pd.merge(pd.read_csv(output_file), pd.read_csv(mapping_file), on='<TICKER>', how='left')
#                     upgraded_file.to_csv(output_file, index=False)
#                 except Exception as error:
#                     return HttpResponse(f'Error reading txt file: {error}', status=500)
#
#             try:
#                 df = pd.read_csv(output_file)
#                 if exchange_filter:
#                     df = df[df['Gielda'] == exchange_filter]
#                 if search_query:
#                     df = df[df['Nazwa'].str.contains(search_query, case=False, na=False)]
#                 paginator = Paginator(df, 20)
#                 page = paginator.get_page(page_number)
#                 rows = page.object_list.to_dict(orient='records')
#             except Exception as error:
#                 return HttpResponse(f'Error reading csv file: {error}', status=500)
#
#             return render(request, 'dashboard.html', {
#                 'rows': rows,
#                 'page': page,
#                 'paginator': paginator,
#                 'search_query': search_query,
#             })


class DashboardView(View):
    def get(self, request):
            date = request.GET.get('date')
            exchange_filter = request.GET.get('exchange')
            page_number = request.GET.get('page', 1)
            if not date:
                return render(request, 'dashboard.html', {'rows': []})

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
                selected_columns = df.iloc[:, [0,10,2,7, 11]]
                if exchange_filter:
                    selected_columns = selected_columns[selected_columns['Gielda'] == exchange_filter]
                paginator = Paginator(selected_columns, 20)
                page = paginator.get_page(page_number)
                rows = page.object_list.to_dict(orient='records')
            except Exception as error:
                return HttpResponse(f'Error reading csv file: {error}', status=500)

            return render(request, 'dashboard.html', {
                'rows': rows,
                'page': page,
                'paginator': paginator,
            })





















