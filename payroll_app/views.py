import re
import json
import os
import subprocess
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from .models import Employee, CustomUser
from .forms import LoginForm, EmployeeForm

def homepage(request):
    """Render the home page with login form"""
    form = LoginForm()
    return render(request, 'payroll_app/employee.html', {'form': form})

def login_view(request):
    """Handle user authentication"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('payroll_app:dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Please correct the errors below')
        return render(request, 'payroll_app/home.html', {'form': form})
    return redirect('payroll_app:homepage')

def employee_records(request):
    """Display all employees and the employee creation form"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('payroll_app:homepage')
        
    employees = Employee.objects.all().order_by('id')
    form = EmployeeForm()
    return render(request, 'payroll_app/Admin.html', {
        'employees': employees,
        'employee_form': form
    })

def create_employee(request):
    """Handle employee creation using the EmployeeForm"""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return JsonResponse({'success': True})
            except IntegrityError:
                return JsonResponse({
                    'success': False,
                    'error': 'Username already exists'
                }, status=400)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        else:
            # Return form validation errors
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=405)


def run_service_java(request):
    """Execute Java service with proper security checks"""
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized', status=401)

    # Security: Validate inputs
    try:
        args = [
            request.GET.get('arg1', 'mayor'),
            request.GET.get('arg2', '160'),
            request.GET.get('arg3', '10'),
            request.GET.get('arg4', '2')
        ]
        
        # Validate arguments
        if not all(re.match(r'^[\w\.-]+$', arg) for arg in args):
            raise ValueError('Invalid arguments')

        java_folder = os.path.join(os.path.dirname(__file__), 'java_files')
        java_filename = 'service.java'
        classname = 'service'

        # Security: Restrict file operations to specific directory
        if not os.path.exists(os.path.join(java_folder, java_filename)):
            return HttpResponse('Service not found', status=404)

        # Compile Java
        compile_result = subprocess.run(
            ['javac', java_filename],
            cwd=java_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if compile_result.returncode != 0:
            return HttpResponse(
                f"Compilation error:\n{compile_result.stderr}",
                status=500
            )

        # Execute Java
        run_result = subprocess.run(
            ['java', classname] + args,
            cwd=java_folder,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        if run_result.returncode != 0:
            return HttpResponse(
                f"Runtime error:\n{run_result.stderr}",
                status=500
            )

        return HttpResponse(f"Java Output:\n\n{run_result.stdout}")

    except subprocess.TimeoutExpired:
        return HttpResponse('Process timed out', status=500)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)