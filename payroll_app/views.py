import re
from django import template
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .forms import loginForm
import subprocess
import os

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
    

def run_service_java(request):
    java_folder = os.path.join(os.path.dirname(__file__), 'java_files')
    java_filename = 'service.java'
    classname = 'service'

    # Sample inputs: "mayor" 160 10 2
    args = ['mayor', '160', '10', '2']

    try:
        # Step 1: Compile
        compile = subprocess.run(
            ['javac', java_filename],
            cwd=java_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if compile.returncode != 0:
            return HttpResponse(f"Compilation error:\n{compile.stderr}", status=500)

        # Step 2: Run
        run = subprocess.run(
            ['java', classname] + args,
            cwd=java_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if run.returncode != 0:
            return HttpResponse(f"Runtime error:\n{run.stderr}", status=500)

        return HttpResponse(f"Java Output:\n\n{run.stdout}")

    except Exception as e:
        return HttpResponse(f"Unexpected error: {str(e)}", status=500)
