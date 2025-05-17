import re
import json
import os
import subprocess
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import IntegrityError
from .models import Employee, CustomUser, Position
from .forms import LoginForm, EmployeeForm

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from typing import Dict, Any
from django.db import transaction

User = get_user_model()

def homepage(request):
    """Render the home page with login form"""
    form = LoginForm()
    return render(request, 'payroll_app/home.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('admin_dashboard' if user.is_staff else 'employee_dashboard')
                else:
                    messages.error(request, 'Account inactive')
            else:
                if not User.objects.filter(username=username).exists():
                    messages.error(request, 'User does not exist')
                else:
                    messages.error(request, 'Invalid password')
        return render(request, 'payroll_app/home.html', {'form': form})
    return render(request, 'payroll_app/home.html', {'form': LoginForm()})

def employee_records(request):
    employees = Employee.objects.all().order_by('id')
    positions = Position.objects.filter(is_active=True).order_by('id')  # Get active positions
    form = EmployeeForm()
    return render(request, 'payroll_app/Admin.html', {
        'employees': employees,
        'employee_form': form,
        'positions': positions,  # Add positions to the context
    })

def get_employee_data(request, employee_id):
    try:
        employee = Employee.objects.select_related('position').get(id=employee_id)
        user = CustomUser.objects.get(employeeID=employee)
        
        response_data = {
            'success': True,
            'employee': {
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'contact': employee.contact,
                'hourly_rate': str(employee.hourly_rate),
                'is_active': employee.is_active,
                'position': {
                    'id': employee.position.id if employee.position else None,
                    'name': employee.position.name if employee.position else None,
                    'standard_hours': employee.position.standard_hours if employee.position else None,
                    'base_salary': str(employee.position.base_salary) if employee.position else None,
                } if employee.position else None
            },
            'user': {
                'username': user.username,
                'is_active': user.is_active
            }
        }
        
        return JsonResponse(response_data)
        
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employee not found'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User account not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def update_employee(request, employee_id):
    if request.method == 'POST':
        try:
            employee = Employee.objects.get(id=employee_id)
            user = CustomUser.objects.get(employeeID=employee)
            
            # Get new username from form
            new_username = request.POST.get('username')
            
            # Check if username is being changed and if it already exists
            if new_username and new_username != user.username:
                if CustomUser.objects.exclude(id=user.id).filter(username=new_username).exists():
                    return JsonResponse({
                        'success': False, 
                        'error': 'Username already exists'
                    })
            
            # Update basic employee info
            employee.first_name = request.POST.get('first_name')
            employee.last_name = request.POST.get('last_name')
            employee.contact = request.POST.get('contact')
            
            # Update position if changed
            position_id = request.POST.get('position')
            if position_id and position_id != 'none':
                position = Position.objects.get(id=position_id)
                employee.position = position
                employee.hourly_rate = position.base_salary
            elif position_id == 'none':
                employee.position = None
            
            # Update active status
            employee.is_active = request.POST.get('is_active', 'off') == 'on'
            employee.save()
            
            # Update user account
            user.username = new_username
            user.is_active = employee.is_active
            password = request.POST.get('password')
            if password:  # Only update password if provided
                user.set_password(password)
            user.save()
            
            return JsonResponse({'success': True, 'refresh': True})
            
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid position selected'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

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

@transaction.atomic
def create_employee(request):
    if request.method == 'POST':
        try:
            # Get form data
            required_fields = ['first_name', 'last_name', 'position', 'contact', 'username', 'password']
            if any(field not in request.POST for field in required_fields):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

            is_active = request.POST.get('is_active', 'false').lower() == 'true'
            
            try:
                position = Position.objects.get(id=request.POST['position'])
            except Position.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid position'}, status=400)

            with transaction.atomic():
                # Create employee
                employee = Employee.objects.create(
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    position=position,
                    hourly_rate=position.base_salary,
                    standard_hours=position.standard_hours,
                    contact=request.POST['contact'],
                    is_active=is_active
                )

                # Create user account
                CustomUser.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password'],
                    role='employee',
                    is_active=is_active,
                    employeeID=employee
                )

            return JsonResponse({
                'success': True,
                'employee': {
                    'id': employee.id,
                    'name': f"{employee.first_name} {employee.last_name}",
                    'position': position.name,
                    'hourly_rate': str(position.base_salary),
                    'status': 'Active' if is_active else 'Inactive'
                }
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

def add_salary_structure(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            standard_hours = int(request.POST.get('standard_hours', 40))
            base_salary = Decimal(request.POST.get('base_salary', 0))
            bonus = Decimal(request.POST.get('bonus', 0))
            deduction = Decimal(request.POST.get('deduction', 0))
            
            # Create new position
            new_position = Position.objects.create(
                name=name,
                standard_hours=standard_hours,
                base_salary=base_salary,
                bonus=bonus,
                deduction=deduction
            )
            
            # Return the new position data as JSON
            return JsonResponse({
                'success': True,
                'position': {
                    'id': new_position.id,
                    'name': new_position.name,
                    'standard_hours': new_position.standard_hours,
                    'base_salary': str(new_position.base_salary),
                    'bonus': str(new_position.bonus),
                    'deduction': str(new_position.deduction),
                }
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def get_position_data(request, position_id):
    try:
        position = Position.objects.get(id=position_id)
        
        response_data = {
            'success': True,
            'position': {
                'id': position.id,
                'name': position.name,
                'standard_hours': position.standard_hours,
                'base_salary': str(position.base_salary),
                'bonus': str(position.bonus),
                'deduction': str(position.deduction),
            }
        }
        
        return JsonResponse(response_data)
        
    except Position.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Position not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def update_salary_structure(request, position_id):
    if request.method == 'POST':
        try:
            position = Position.objects.get(id=position_id)
            
            # Update position data
            position.name = request.POST.get('name')
            position.standard_hours = int(request.POST.get('standard_hours', 40))
            position.base_salary = Decimal(request.POST.get('base_salary'))
            position.bonus = Decimal(request.POST.get('bonus', 0))
            position.deduction = Decimal(request.POST.get('deduction', 0))
            
            position.save()
            
            return JsonResponse({'success': True})
            
        except Position.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Position not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_salary_structure(request, position_id):
    try:
        position = Position.objects.get(id=position_id)
        
        # Check if any employees are using this position
        if Employee.objects.filter(position=position).exists():
            return JsonResponse({
                'success': False, 
                'error': 'Cannot delete this position because it is assigned to one or more employees.'
            })
            
        position.delete()
        return JsonResponse({'success': True})
        
    except Position.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Position not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


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
    
def logout(request):
    return render(request, 'payroll_app/home.html')
def home_page(request):
    return render(request, 'payroll_app/home.html')
def employee_dashboard(request):
    return render(request, 'payroll_app/employee.html')
def admin_dashboard(request):
    positions = Position.objects.all().order_by('name')
    return render(request, 'payroll_app/admin.html', {'positions': positions})

    return render(request, 'admin.html', {'employees': employees})