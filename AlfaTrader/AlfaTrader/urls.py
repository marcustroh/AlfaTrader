"""
URL configuration for AlfaTrader project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from AlfaTrader_App import views as at_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', at_views.BaseView.as_view(), name='base'),
    path('', at_views.StartView.as_view(), name='start'),
    # path('main/', at_views.MainView.as_view(), name='main'),
    path('login/', at_views.UserLoginView.as_view(), name='login'),
    path('register/', at_views.UserRegisterView.as_view(), name='register'),
    path('logout/', at_views.LogoutUserView.as_view(), name='logout'),
    path('dashboard3/', at_views.DashboardView3.as_view(), name='dashboard3'),
    path('dashboard/<str:ticker>', at_views.TickerDetailsView.as_view(), name='ticker_detail'),
    path('buy_transaction/', at_views.BuyTransactionView.as_view(), name='buy_transaction'),
    path('sell_transaction/', at_views.SellTransactionView.as_view(), name='sell_transaction'),
    path('transactions/', at_views.TransactionsView.as_view(), name='transactions'),
    path('about_author/', at_views.AboutAuthor.as_view(), name='about_author'),
    path('contact/', at_views.ContactDetails.as_view(), name='contact_details'),
    path('about_app/', at_views.AboutApp.as_view(), name='about_app'),
    path('how_to_begin/', at_views.HowToBegin.as_view(), name='how_to_begin'),
    path('portfolios/', at_views.PortfoliosView.as_view(), name='portfolios'),
    path('portfolios/create/', at_views.PortfolioCreateView.as_view(), name='portfolio_create'),
    path('portfolios/modify/<int:portfolio_id>/', at_views.PortfolioModifyView.as_view(), name='portfolio_modify'),
    path('portfolios/delete/<int:portfolio_id>/', at_views.PortfolioDeleteView.as_view(), name='portfolio_delete'),

]





















