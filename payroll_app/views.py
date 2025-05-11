import re
import subprocess
import os
from django import template
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader

from payroll_project.payroll_app.models import Employee
from .forms import loginForm
from payroll_app.models import Employee
from .forms import EmployeeForm 
from django.http import JsonResponse

def homepage(request):
    return render(request, 'payroll_app/home.html')

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

def employee_records(request):
    employees = Employee.objects.all().order_by('id')
    form = EmployeeForm()
    return render(request, 'payroll_app/Admin.html', {
        'employees': employees,
        'employee_form': form
    })
    
def create_employee(request):
    if request.method == 'POST':
        try:
            employee = Employee(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                position=request.POST.get('position'),
                hourly_rate=request.POST.get('hourly_rate'),
                standard_hours=request.POST.get('standard_hours'),
                contact=request.POST.get('contact')
            )
            employee.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})    

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

