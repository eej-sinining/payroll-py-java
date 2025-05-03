import re
from django import template
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .forms import loginForm

def homepage(request):
    return render(request, 'payroll_app/Admin.html')

def login_view(request):
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('payroll_app:dashboard')
            else:
                form.add_error(None, 'Invalid Credentials')

        return render(request, 'payroll_app/home.html', {'form': form})
 # Or whichever page you want as default        