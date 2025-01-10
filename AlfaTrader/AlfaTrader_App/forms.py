from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Portfolio, PortfolioStocks, Transactions, UserStocksBalance, Stocks


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        nick = cd.get('username')
        pwd = cd.get('password')
        user = authenticate(username=nick, password=pwd)
        if user is None:
            raise ValidationError('Incorrect password or login!')
        else:
            self.user = user

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password != password_confirm:
            raise forms.ValidationError("Passwords are not the same!")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class PortfolioForm(forms.Form):
    portfolio_name = forms.CharField(max_length=255, required=True)
    stock = forms.ModelMultipleChoiceField(
        queryset=UserStocksBalance.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PortfolioForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['stock'].queryset = UserStocksBalance.objects.filter(user=user)

class PortfolioModifyForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name']

    stocks = forms.ModelMultipleChoiceField(
        queryset=UserStocksBalance.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PortfolioModifyForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['stocks'].queryset = UserStocksBalance.objects.filter(user=user)





















