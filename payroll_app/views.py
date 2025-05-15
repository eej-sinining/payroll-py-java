
import os
import subprocess
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError

from .models import Employee, CustomUser, Position
from .forms import LoginForm, EmployeeForm 
from django.http import JsonResponse

def homepage(request):
    return render(request, 'payroll_app/home.html')

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
    positions = Position.objects.filter(is_active=True).order_by('name')  # Get active positions
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
        try:
            # First create the Employee
            employee = Employee(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                position=request.POST.get('position'),
                hourly_rate=request.POST.get('hourly_rate'),
                standard_hours=request.POST.get('standard_hours'),
                contact=request.POST.get('contact')
            )
            employee.save()
            
            # Then create the CustomUser account
            user = CustomUser.objects.create_user(
                username=request.POST.get('username'),
                password=request.POST.get('password'),
                role='employee',  # or whatever default role you want
                is_active=request.POST.get('is_active', 'off') == 'on',
                employeeID=employee  # link the user to the employee
            )
            
            return JsonResponse({'success': True})
        except IntegrityError as e:
            # If employee was created but user creation failed, delete the employee
            if 'employee' in locals():
                employee.delete()
            return JsonResponse({'success': False, 'error': 'Username already exists'})
        except Exception as e:
            # Clean up if anything fails
            if 'employee' in locals():
                employee.delete()
            if 'user' in locals():
                user.delete()
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'}) 


def add_salary_structure(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            standard_hours = int(request.POST.get('standard_hours', 40))
            base_salary = Decimal(request.POST.get('base_salary'))
            bonus = Decimal(request.POST.get('bonus', 0))
            deduction = Decimal(request.POST.get('deduction', 0))
            
            # Create new position with salary structure
            Position.objects.create(
                name=name,
                standard_hours=standard_hours,
                base_salary=base_salary,
                bonus=bonus,
                deduction=deduction
            )
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# def run_service_java(request):
#     java_folder = os.path.join(os.path.dirname(__file__), 'java_files')
#     java_filename = 'service.java'
#     classname = 'service'

#     # Security: Restrict file operations to specific directory
#     try:
#         if not os.path.exists(os.path.join(java_folder, java_filename)):
#             return HttpResponse('Service not found', status=404)

#         # Compile Java
#         compile_result = subprocess.run(
#             ['javac', java_filename],
#             cwd=java_folder,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=10
#         )
#         if compile_result.returncode != 0:
#             return HttpResponse(
#                 f"Compilation error:\n{compile_result.stderr}",
#                 status=500
#             )

#         # Execute Java
#         run_result = subprocess.run(
#             ['java', classname] + args,
#             cwd=java_folder,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True,
#             timeout=10
#         )
#         if run_result.returncode != 0:
#             return HttpResponse(
#                 f"Runtime error:\n{run_result.stderr}",
#                 status=500
#             )

#         return HttpResponse(f"Java Output:\n\n{run_result.stdout}")

#     except subprocess.TimeoutExpired:
#         return HttpResponse('Process timed out', status=500)
#     except Exception as e:
#         return HttpResponse(f"Error: {str(e)}", status=500)
def run_service_java(request):
    # Get parameters from request if needed
    args = request.GET.getlist('args', [])  # Example: get arguments from query string
    
    java_folder = os.path.join(os.path.dirname(__file__), 'java_files')
    java_filename = 'service.java'
    classname = 'service'

    # Security: Restrict file operations to specific directory
    try:
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
def delete_employee(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # Delete the associated CustomUser if it exists
        try:
            custom_user = CustomUser.objects.get(employeeID=employee)
            custom_user.delete()
        except CustomUser.DoesNotExist:
            pass  # No user associated, continue with employee deletion
            
        employee.delete()
        return JsonResponse({'success': True})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})