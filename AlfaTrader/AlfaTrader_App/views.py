from django.shortcuts import render
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, logout
from django.views.generic import CreateView
from django.urls import reverse_lazy

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

class DashboardView(View):
    def get(self, request):
        return render(request, 'dashboard.html')



















